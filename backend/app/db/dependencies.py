from typing import AsyncGenerator

from app.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request


def get_sync_db_session():
    sync_engine = create_engine(str(settings.db_sync_url), echo=True)
    sync_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sync_engine,
    )
    return sync_session()


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
