import logging
import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from server.src.settings import Settings

settings = Settings()
connect_url = str(settings.db_url)

engine = create_async_engine(connect_url, echo=True, future=True)


# def init_db():
#     SQLModel.metadata.create_all(engine)

async def database_exists(db_name):
    async with engine.begin() as conn:
        result = await conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = :name",
            {"name": db_name}
        )
        return result.scalar() is not None


async def init_db():
    logging.debug("Startup scripts - init_db")
    # async with engine.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.drop_all)
    #     await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
