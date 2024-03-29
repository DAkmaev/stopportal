from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from starlette.requests import Request

from app.settings import settings


def get_sync_db_session() -> sessionmaker[Session]:
    sync_engine = create_engine(str(settings.db_url), echo=True)
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sync_engine,
    )

async def get_db_session(request: Request = None) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.

    :param request: current request.
    :yield: database session.
    """
    session: AsyncSession = request.app.state.db_session_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()

