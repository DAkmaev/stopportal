from typing import List, Optional

from app.db.dao.stops import StopsDAO
from app.db.dao.strategies import StrategiesDAO
from app.db.dependencies import get_db_session
from app.db.models.company import CompanyModel
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CompanyDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session
        self.stop_dao = StopsDAO(session)
        self.strategy_dao = StrategiesDAO(session)

    async def create_company_model(
        self,
        tiker: str,
        name: str,
        company_type: str,
        strategies: list[int] = None,
    ) -> CompanyModel:
        raw_company = await self.session.execute(
            select(CompanyModel).where(CompanyModel.tiker == tiker),
        )
        exist_company: CompanyModel = raw_company.scalars().one_or_none()

        if exist_company:
            raise HTTPException(
                status_code=400,
                detail=f"Компания {exist_company.tiker} уже существует",
            )

        company = CompanyModel(tiker=tiker, name=name, type=company_type)
        self.session.add(company)
        return company

    async def create_companies_models(self, items: List[CompanyModel]) -> None:
        new_tikers = [item.tiker for item in items]

        raw_companies = await self.session.execute(
            select(CompanyModel).where(CompanyModel.tiker.in_(new_tikers)),
        )
        exist_companies = list(raw_companies.scalars().fetchall())

        if exist_companies:
            exist_companies_tikers_str = ",".join(
                [comp.tiker for comp in exist_companies],
            )
            raise HTTPException(
                status_code=400,
                detail=f"В базе уже есть тикеры {exist_companies_tikers_str}",
            )

        self.session.add_all(items)

    async def update_company_model(
        self,
        company_id: int,
        updated_fields: dict,
        partial: bool = False,
    ) -> CompanyModel:
        company = await self.get_company_model(company_id)

        if not company:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        # Extract Strategies data if present and handle updates
        strategies_data = updated_fields.pop("strategies", None)
        if strategies_data is not None:
            updated_strategies_ids = {strategy["id"] for strategy in strategies_data}
            company.strategies = [
                await self.strategy_dao.get_strategy_model(strategy_id)
                for strategy_id in updated_strategies_ids
            ]

        # Update other fields if specified and allowed
        for field, value in updated_fields.items():
            if not partial or (field in company.__dict__ and value is not None):
                setattr(company, field, value)

        return company

    async def delete_company_model(self, company_id: int) -> None:
        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Акция не найдена")

        await self.session.delete(company)

    async def get_all_companies(
        self,
        limit: int = 10000,
        offset: int = 0,
    ) -> List[CompanyModel]:
        raw_companies = await self.session.execute(
            select(CompanyModel).limit(limit).offset(offset),
        )

        return list(raw_companies.scalars().fetchall())

    async def get_company_model(self, company_id: int) -> CompanyModel:
        company = await self.session.execute(
            select(CompanyModel).where(CompanyModel.id == company_id),
        )

        return company.scalars().one_or_none()

    async def get_company_model_by_tiker(self, tiker: str) -> CompanyModel:
        company = await self.session.execute(
            select(CompanyModel).where(CompanyModel.tiker == tiker),
        )

        return company.scalars().one_or_none()

    async def filter(
        self,
        tiker: Optional[str] = None,
    ) -> List[CompanyModel]:
        query = select(CompanyModel)
        if tiker:
            query = query.where(CompanyModel.tiker == tiker)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
