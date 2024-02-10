from typing import List, Optional

from app.db.dependencies import get_db_session
from app.db.models.dummy_model import DummyModel
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class DummyDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_dummy_model(self, name: str) -> None:
        self.session.add(DummyModel(name=name))

    async def get_all_dummies(self, limit: int, offset: int) -> List[DummyModel]:
        raw_dummies = await self.session.execute(
            select(DummyModel).limit(limit).offset(offset),
        )

        return list(raw_dummies.scalars().fetchall())

    async def filter(
        self,
        name: Optional[str] = None,
    ) -> List[DummyModel]:
        query = select(DummyModel)
        if name:
            query = query.where(DummyModel.name == name)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
