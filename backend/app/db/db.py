import logging
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request

from backend.app.settings import Settings

settings = Settings()
connect_url = str(settings.db_url)

engine = create_async_engine(
    str(settings.db_url),
    echo=False,
)


SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def init_db(app: FastAPI):
    logging.debug("Startup scripts - init_db")
    app.state.db_engine = engine
    app.state.db_session_factory = SessionLocal
    logging.debug("Finish script - init_db")


async def get_session(request: Request = None) -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = request.app.state.db_session_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()
