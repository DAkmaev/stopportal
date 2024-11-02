from server.src.db.db import get_session
from server.src.db.models.company import CompanyModel, StopModel
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class StopsDAO:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_stop_model(self, stop_id: int) -> StopModel:
        company = await self.session.execute(
            select(StopModel).where(StopModel.id == stop_id),
        )

        return company.scalars().one_or_none()

    async def add_stop_model(
        self,
        company_id: int,
        period: str,
        value: float,
    ) -> StopModel:
        raw_stop = await self.session.execute(
            select(StopModel).where(
                StopModel.company_id == company_id,
                StopModel.period == period,
            ),
        )
        existing_stop: StopModel = raw_stop.scalars().one_or_none()

        if existing_stop:
            raise HTTPException(
                status_code=400,
                detail="Стоп с таким периодом уже существует для данной компании",
            )

        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Акция не найдена")

        stop = StopModel(period=period, value=value)
        company.stops.append(stop)
        return stop

    async def update_stop_model(self, stop_data: dict) -> StopModel:  # noqa:WPS210
        stop_id = stop_data.get("id")
        period = stop_data.get("period")
        company_id = stop_data.get("company_id")

        raw_stop = await self.session.execute(
            select(StopModel).where(
                StopModel.id != stop_id,
                StopModel.period == period,
                StopModel.company_id == company_id,
            ),
        )
        existing_stop: StopModel = raw_stop.scalars().one_or_none()
        if existing_stop:
            raise HTTPException(
                status_code=400,
                detail="Стоп с такими параметрами уже существует",
            )

        stop = await self.get_stop_model(stop_id)
        if stop:
            for field, value in stop_data.items():
                setattr(stop, field, value)
            return stop

        # If stop_id is not provided or stop with given id is not found, create a
        # new stop
        stop = StopModel(**stop_data)
        self.session.add(stop)
        return stop

    async def delete_stop_model(self, stop_id: int) -> None:
        stop = await self.session.get(StopModel, stop_id)
        if not stop:
            raise HTTPException(status_code=404, detail="Стоп не найден")

        await self.session.delete(stop)
