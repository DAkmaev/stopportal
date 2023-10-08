from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.dependencies import get_db_session
from fastapi import Depends, HTTPException
from typing import List, Optional, Type

from backend.db.models.companies import CompanyModel, CompanyStopModel


class CompanyDAO:
    """Class for accessing company table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_company_model(self, tiker: str, type: str) -> None:
        """
        Add single company to session.

        :param tiker: tiker of a company.
        :param type: type of company:  MOEX or YAHOO.
        """
        raw_company = await self.session.execute(
            select(CompanyModel).where(CompanyModel.tiker == tiker)
        )
        exist_company: CompanyModel = raw_company.scalars().one_or_none()

        if exist_company:
            raise HTTPException(status_code=400,
                                detail=f"Тикер {exist_company.tiker} уже существует")

        self.session.add(CompanyModel(tiker=tiker, type=type))

    async def create_companies_models(self, items: List[CompanyModel]) -> None:
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

    async def add_stop_model(self, company_id: int, period: str, value: float) -> Type[CompanyModel]:
        """
        Add stop to company.

        :param value:
        :param period:
        :param company_id:
        """
        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Акция не найдена")

        company.stops.append(CompanyStopModel(period=period, value=value))

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

    async def delete_company_stop_model(self, stop_id: int, company_id: int) -> None:
        """
        Delete company_stop in session.
        :param company_id:
        :param stop_id:
        """
        stop = await self.session.get(CompanyStopModel, stop_id)
        if not stop:
            raise HTTPException(status_code=404, detail="Стоп не найден")

        if stop.company_id != company_id:
            raise HTTPException(status_code=400, detail="Стоп id не от данной акции")

        await self.session.delete(stop)

    async def get_all_companies(self, limit: int = 100,
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
            select(CompanyModel).where(id == id)
        )

        return company.scalars().one_or_none()

    async def get_company_stop_model(self, id: int) -> CompanyStopModel:
        """
        Get company stop models by id.

        :param id: company stop id.
        :return: company.
        """
        company = await self.session.execute(
            select(CompanyStopModel).where(id == id)
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
