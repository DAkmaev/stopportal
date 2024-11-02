import logging
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request

from server.src.settings import Settings

settings = Settings()
connect_url = str(settings.db_url)


async def init_db(app: FastAPI):
    logging.debug("Startup scripts - init_db")
    engine = create_async_engine(str(settings.db_url), echo=False)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


async def get_session(request: Request = None) -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = request.app.state.db_session_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()
