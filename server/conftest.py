from typing import AsyncGenerator, Any

import pytest
from celery import Celery
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from server.src.main import app
from server.src.db.db import get_session, settings
from server.src.db.utils import create_database, drop_database
from server.tests.utils.common import (
    get_superuser_token_headers,
    get_user_token_headers,
    get_inactive_user_token_headers,
)


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from server.src.db.models import load_all_models  # noqa: WPS433

    load_all_models()

    await create_database()

    # connect_str = "sqlite+aiosqlite:///test.db"
    engine = create_async_engine(str(settings.db_test_url))

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncSession:
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
) -> FastAPI:
    application = app
    application.dependency_overrides[get_session] = lambda: dbsession
    return application  # noqa: WPS331


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def celery_app():
    celery_app = Celery("tasks", broker="memory://", backend="memory://")
    celery_app.conf.task_always_eager = True
    return celery_app


@pytest.fixture
def celery_local_app():
    celery_app = Celery(
        "tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1"
    )
    celery_app.conf.update(
        task_always_eager=False,  # Отключаем eager-режим
        task_eager_propagates=True,
        task_store_eager_result=False,
        task_ignore_result=False,
        task_store_errors_even_if_ignored=True,
    )
    return celery_app


@pytest.fixture()
async def superuser_token_headers(
    client: AsyncClient,
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> dict[str, Any]:
    return await get_superuser_token_headers(client, fastapi_app, dbsession)


@pytest.fixture()
async def user_token_headers(
    client: AsyncClient,
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> dict[str, Any]:
    return await get_user_token_headers(client, fastapi_app, dbsession)


@pytest.fixture()
async def user_inactive_token_headers(
    client: AsyncClient,
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> dict[str, str]:
    return await get_inactive_user_token_headers(client, fastapi_app, dbsession)
