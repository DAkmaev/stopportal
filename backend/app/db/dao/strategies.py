from typing import List

from app.db.dependencies import get_db_session
from app.db.models.company import StrategyModel
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


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

    async def get_all_strategies_model(self) -> List[StrategyModel]:
        """
        Get all strategies models with limit/offset pagination.
        :return: stream of strategies.
        """
        raw_strategies = await self.session.execute(
            select(StrategyModel),
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

    async def update_strategy_model(
        self, strategy_id: int, name: str, description: str
    ) -> StrategyModel:
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
