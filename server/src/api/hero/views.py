from typing import Annotated

from fastapi import Depends, Query, APIRouter
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from server.src.db.db import get_session
from server.src.db.models.hero import HeroModel

router = APIRouter()


@router.get("/heroes")
async def read_heroes(
        session: AsyncSession = Depends(get_session),
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
) -> list[HeroModel]:
    result = await session.execute(select(HeroModel).offset(offset).limit(limit))
    heroes = result.scalars().all()
    return heroes


@router.post("/heroes/")
async def create_hero(
        hero: HeroModel,
        session: AsyncSession = Depends(get_session),

) -> HeroModel:
    session.add(hero)
    # await session.commit()
    # await session.refresh(hero)
    return hero