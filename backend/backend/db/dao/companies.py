from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.dependencies import get_db_session
from fastapi import Depends, HTTPException
from typing import List, Optional, Type

from backend.db.models.company import CompanyModel, StopModel, StrategyModel
from backend.db.dao.stops import StopsDAO
from backend.db.dao.strategies import StrategiesDAO


class CompanyDAO:
    """Class for accessing company table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session
        self.stop_dao = StopsDAO(session)
        self.strategy_dao = StrategiesDAO(session)

    async def create_company_model(self, tiker: str, name: str, type: str, strategies: list[int] = None) -> CompanyModel:
        """
        Add single company to session.

        :param name:
        :param tiker: tiker of a company.
        :param type: type of company:  MOEX or YAHOO.
        """
        raw_company = await self.session.execute(
            select(CompanyModel).where(CompanyModel.tiker == tiker)
        )
        exist_company: CompanyModel = raw_company.scalars().one_or_none()

        if exist_company:
            raise HTTPException(status_code=400,
                                detail=f"Компания {exist_company.tiker} уже существует")


        company = CompanyModel(tiker=tiker, name=name, type=type)
        self.session.add(company)
        return company

    async def create_companies_models(
        self, items: List[CompanyModel]) -> None:
        """
        Add multiple companies to session.

        :param items:
        """
        new_tikers = map(lambda i: i.tiker, items)

        raw_companies = await self.session.execute(
            select(CompanyModel).where(CompanyModel.tiker.in_(new_tikers))
        )
        exist_companies = list(raw_companies.scalars().fetchall())

        if len(exist_companies) > 0:
            exist_companies_tikers = map(lambda i: i.tiker, exist_companies)
            raise HTTPException(status_code=400,
                                detail=f"В базе уже есть тикеры {','.join(exist_companies_tikers)}")

        self.session.add_all(items)

    async def update_company_model(
        self, company_id: int, updated_fields: dict, partial: bool = False
    ) -> CompanyModel:
        """
        Update company model in the session.
        """
        company = await self.get_company_model(company_id)

        if not company:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        # Extract Strategies data if present and handle updates
        strategies_data = updated_fields.pop("strategies", None)
        if strategies_data is not None:
            updated_strategies_ids = {strategy['id'] for strategy in
                                      strategies_data}
            company.strategies = [
                await self.strategy_dao.get_strategy_model(strategy_id)
                for strategy_id in updated_strategies_ids
            ]

        # Update other fields if specified and allowed
        for field, value in updated_fields.items():
            if not partial or (hasattr(company, field) and value is not None):
                setattr(company, field, value)

        return company

    async def delete_company_model(self, company_id: int) -> None:
        """
        Delete company in session.
        :param company_id:
        """
        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Акция не найдена")

        await self.session.delete(company)

    async def get_all_companies(self, limit: int = 10000,
                                offset: int = 0) -> List[CompanyModel]:
        """
        Get all companies models with limit/offset pagination.

        :param limit: limit of dummies.
        :param offset: offset of dummies.
        :return: stream of companies.
        """
        raw_companies = await self.session.execute(
            select(CompanyModel).limit(limit).offset(offset),
        )

        return list(raw_companies.scalars().fetchall())

    async def get_company_model(self, id: int) -> CompanyModel:
        """
        Get company models by id.

        :param id: company id.
        :return: company.
        """
        company = await self.session.execute(
            select(CompanyModel).where(CompanyModel.id == id)
        )

        return company.scalars().one_or_none()

    async def get_company_model_by_tiker(self, tiker: str) -> CompanyModel:
        """
        Get specific company model by tiker.

        :param tiker: tiker of company instance.
        :return: company model.
        """
        company = await self.session.execute(
            select(CompanyModel).where(CompanyModel.tiker == tiker)
        )

        return company.scalars().one_or_none()

    async def filter(
        self,
        tiker: Optional[str] = None,
    ) -> List[CompanyModel]:
        """
        Get specific company model.

        :param tiker: tiker of company instance.
        :return: company models.
        """
        query = select(CompanyModel)
        if tiker:
            query = query.where(CompanyModel.tiker == tiker)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
