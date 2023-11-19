from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.dependencies import get_db_session
from fastapi import Depends, HTTPException

from backend.db.models.companies import CompanyModel, StopModel


class StopsDAO:
    """Class for accessing company table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_company_stop_model(self, id: int) -> StopModel:
        """
        Get company stop models by id.

        :param id: company stop id.
        :return: company.
        """
        company = await self.session.execute(
            select(StopModel).where(StopModel.id == id)
        )

        return company.scalars().one_or_none()

    async def add_stop_model(self, company_id: int, period: str,
                             value: float) -> StopModel:
        """
        Add stop to company.

        :param value:
        :param period:
        :param company_id:
        """
        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Акция не найдена")

        stop = StopModel(period=period, value=value)
        company.stops.append(stop)
        return stop

    async def update_company_stop(self, company_id: int, stop_data: dict) -> StopModel:
        stop_id = stop_data.get("id")
        if stop_id:
            stop = await self.get_company_stop_model(stop_id)
            if stop:
                for field, value in stop_data.items():
                    setattr(stop, field, value)
                return stop

        # If stop_id is not provided or stop with given id is not found, create a new stop
        stop = StopModel(**stop_data, company_id=company_id)
        self.session.add(stop)
        return stop

    async def delete_company_stop_model(self, stop_id: int) -> None:
        """
        Delete stop in session.
        :param stop_id:
        """
        stop = await self.session.get(StopModel, stop_id)
        if not stop:
            raise HTTPException(status_code=404, detail="Стоп не найден")

        await self.session.delete(stop)
