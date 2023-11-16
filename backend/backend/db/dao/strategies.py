from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.dependencies import get_db_session
from fastapi import Depends, HTTPException

from backend.db.models.companies import StrategyModel, CompanyModel


class StrategiesDAO:
    """Class for accessing Strategies table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_strategy_model(self, name: str, description: str) -> StrategyModel:
        """
        Add strategy model.

        """

        strategy = StrategyModel(name=name, description=description)
        self.session.add(strategy)
        return strategy

    async def get_strategy_model(self, id: int) -> StrategyModel:
        """
        Get strategy model.

        """
        strategy = await self.session.get(StrategyModel, id)

        if not strategy:
            raise HTTPException(status_code=404, detail="Запись о стратегии не найдена")

        return strategy

    async def get_all_strategies_model(self, limit: int = 100,
                                       offset: int = 0) -> List[StrategyModel]:
        """
        Get all strategies models with limit/offset pagination.

        :param limit: limit of strategies.
        :param offset: offset of strategies.
        :return: stream of strategies.
        """
        raw_strategies = await self.session.execute(
            select(StrategyModel).limit(limit).offset(offset),
        )

        return list(raw_strategies.scalars().fetchall())

    async def get_strategy_model_by_name(self, name: str) -> StrategyModel:
        """
        Get strategy model by name.

        """

        strategy = await self.session.execute(
            select(StrategyModel).where(StrategyModel.name == name)
        )

        return strategy.scalars().one_or_none()

    async def delete_strategy_model(self, strategy_id: int) -> None:
        """
        Delete strategy_mode in session.
        :param strategy_id:
        """
        strategy = await self.session.get(StrategyModel, strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Стратегия не найдена")


        await self.session.delete(strategy)

    async def update_strategy_model(self, strategy_id: int, name: str, description: str) -> StrategyModel:
        """
        Update strategy model by ID.

        """
        strategy = await self.session.get(StrategyModel, strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Стратегия не найдена")

        strategy.name = name
        strategy.description = description
        self.session.add(strategy)
        return strategy

    # COMPANY
    async def add_strategy_to_company(self, company_id: int, strategy_id: int) -> CompanyModel:
        """
        Add strategy to company.
        :param strategy_id:
        :param company_id:
        """
        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        strategy = await self.session.get(StrategyModel, strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Стратегия не найдена")

        if strategy in company.strategies:
            raise HTTPException(status_code=400, detail="Стратегия уже добавлена")

        company.strategies.append(strategy)
        return company

    async def update_strategies_in_company(self, company_id: int,
                                           strategy_ids: List[int]) -> CompanyModel:
        """
        Update strategies in company.
        :param company_id:
        :param strategy_ids: List of strategy IDs to replace in the company
        """
        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        strategies = []
        for strategy_id in strategy_ids:
            strategy = await self.session.get(StrategyModel, strategy_id)
            if not strategy:
                raise HTTPException(status_code=404,
                                    detail=f"Стратегия с ID {strategy_id} не найдена")
            strategies.append(strategy)

        # Замена списка стратегий в компании на новый список по переданным ID
        company.strategies = strategies

        return company

    async def remove_strategy_from_company(self, company_id: int,
                                           strategy_id: int) -> CompanyModel:
        """
        Remove strategy from company.
        :param company_id:
        :param strategy_id: ID of the strategy to remove from the company
        """
        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        strategy_to_remove = None
        for strategy in company.strategies:
            if strategy.id == strategy_id:
                strategy_to_remove = strategy
                break

        if strategy_to_remove:
            company.strategies.remove(strategy_to_remove)
        else:
            raise HTTPException(status_code=404,
                                detail=f"Стратегия с ID {strategy_id} не найдена в компании")

        return company

    # async def update_company_stop(self, company_id: int, stop_data: dict) -> CompanyStopModel:
    #     stop_id = stop_data.get("id")
    #     if stop_id:
    #         stop = await self.get_company_stop_model(stop_id)
    #         if stop:
    #             for field, value in stop_data.items():
    #                 setattr(stop, field, value)
    #             return stop
    #
    #     # If stop_id is not provided or stop with given id is not found, create a new stop
    #     stop = CompanyStopModel(**stop_data, company_id=company_id)
    #     self.session.add(stop)
    #     return stop
    #
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
