import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.tests.utils.common import (random_lower_string, create_test_user,
                                    get_superuser_token_headers)


@pytest.mark.anyio
async def test_login_access_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    password = random_lower_string()
    user = await create_test_user(dbsession, password=password)

    url = fastapi_app.url_path_for("login_access_token")
    response = await client.post(
        url,
        data={
            "username": user.name,
            "password": password,
        },
    )
    token = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(token, dict)
    assert 'access_token' in token


@pytest.mark.anyio
async def test_use_access_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    superuser_token_headers: dict[str, str]
) -> None:
    url = fastapi_app.url_path_for("test_token")
    response = await client.post(url, headers=superuser_token_headers)

    result = response.json()
    assert response.status_code == 200
    assert "email" in result


@pytest.mark.anyio
async def test_use_access_token_no_access(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, str]
) -> None:
    url = fastapi_app.url_path_for("test_token")
    response = await client.post(url, headers=user_token_headers)

    result = response.json()
    assert response.status_code == 403
    assert result["detail"] == "Not enough permissions"
