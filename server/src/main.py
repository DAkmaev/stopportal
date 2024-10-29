import logging
from typing import Annotated

from fastapi import Depends, FastAPI, Query

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from server.src.db.db import get_session, init_db
from server.src.db.models.hero import HeroModel
from server.src.settings import settings

logging.basicConfig(
    level=logging.getLevelName(settings.log_level.value),
    format="%(levelname)s:     %(message)s",  # noqa: WPS323
    #format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",  # noqa: WPS323
)
logger = logging.getLogger("stopportal")

app = FastAPI(
    logging=logging,
)


@app.on_event("startup")
async def on_startup():
    logger.info("Startup block")
    await init_db(app)


@app.post("/heroes/")
async def create_hero(
        session: AsyncSession = Depends(get_session),
) -> HeroModel:
    hero = HeroModel(name="aaaa2", secret_name="bbb3")
    session.add(hero)
    return hero


@app.get("/heroes/")
async def read_heroes(
        session: AsyncSession = Depends(get_session),
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
) -> list[HeroModel]:
    result = await session.execute(select(HeroModel).offset(offset).limit(limit))
    heroes = result.scalars().all()
    return heroes


# @app.get("/heroes/{hero_id}")
# def read_hero(hero_id: int, session: SessionDep) -> Hero:
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     return hero
#
#
# @app.delete("/heroes/{hero_id}")
# def delete_hero(hero_id: int, session: SessionDep):
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     session.delete(hero)
#     session.commit()
#     return {"ok": True}