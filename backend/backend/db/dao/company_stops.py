from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.dependencies import get_db_session
from fastapi import Depends, HTTPException

from backend.db.models.companies import CompanyModel, CompanyStopModel


class CompanyStopsDAO:
    """Class for accessing company table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_company_stop_model(self, id: int) -> CompanyStopModel:
        """
        Get company stop models by id.

        :param id: company stop id.
        :return: company.
        """
        company = await self.session.execute(
            select(CompanyStopModel).where(CompanyStopModel.id == id)
        )

        return company.scalars().one_or_none()

    async def add_stop_model(self, company_id: int, period: str, value: float) -> CompanyStopModel:
        """
        Add stop to company.

        :param value:
        :param period:
        :param company_id:
        """
        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Акция не найдена")

        stop = CompanyStopModel(period=period, value=value)
        company.stops.append(stop)
        return stop

    async def update_company_stop(self, company_id: int, stop_data: dict) -> CompanyStopModel:
        stop_id = stop_data.get("id")
        if stop_id:
            stop = await self.get_company_stop_model(stop_id)
            if stop:
                for field, value in stop_data.items():
                    setattr(stop, field, value)
                return stop

        # If stop_id is not provided or stop with given id is not found, create a new stop
        stop = CompanyStopModel(**stop_data, company_id=company_id)
        self.session.add(stop)
        return stop

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
