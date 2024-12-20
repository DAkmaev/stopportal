from typing import List

from backend.app.db.db import get_session
from backend.app.db.models.company import StrategyModel
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class StrategiesDAO:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def create_strategy_model(
        self,
        name: str,
        description: str,
        user_id: int,
    ) -> StrategyModel:
        strategy = StrategyModel(name=name, description=description, user_id=user_id)
        self.session.add(strategy)
        return strategy

    async def get_strategy_model(self, strategy_id: int) -> StrategyModel:
        strategy = await self.session.get(StrategyModel, strategy_id)

        if not strategy:
            raise HTTPException(status_code=404, detail="Запись о стратегии не найдена")

        return strategy

    async def get_all_strategies_model(self, user_id: int) -> List[StrategyModel]:
        raw_strategies = await self.session.execute(
            select(StrategyModel).where(StrategyModel.user_id == user_id),
        )

        return list(raw_strategies.scalars().fetchall())

    async def get_strategy_model_by_name(self, name: str) -> StrategyModel:
        strategy = await self.session.execute(
            select(StrategyModel).where(StrategyModel.name == name),
        )

        return strategy.scalars().one_or_none()

    async def delete_strategy_model(self, strategy_id: int) -> None:
        strategy = await self.session.get(StrategyModel, strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Стратегия не найдена")

        await self.session.delete(strategy)

    async def update_strategy_model(
        self,
        strategy_id: int,
        name: str,
        description: str,
    ) -> StrategyModel:
        strategy = await self.session.get(StrategyModel, strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Стратегия не найдена")

        strategy.name = name
        strategy.description = description
        self.session.add(strategy)
        return strategy
