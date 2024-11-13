import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from server.tests.utils.common import create_test_user


@pytest.mark.anyio
async def test_create_hero(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    response = await client.get("/api/heroes/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_root(
    client: AsyncClient,
    dbsession: AsyncSession,
):
    response = await client.get("/api/health")
    assert response.status_code == 200

    user = await create_test_user(dbsession, name="AAA")

    assert user.name
