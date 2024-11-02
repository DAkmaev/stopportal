from typing import Any

import pytest
from server.tests.utils.common import create_test_user, random_lower_string
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


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
    assert "access_token" in token


@pytest.mark.anyio
async def test_use_access_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    url = fastapi_app.url_path_for("test_token")
    response = await client.post(url, headers=user_token_headers["headers"])

    result = response.json()
    assert response.status_code == 200
    assert "email" in result


@pytest.mark.anyio
async def test_use_access_token_no_access(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    url = fastapi_app.url_path_for("test_token")
    response = await client.post(url)

    result = response.json()
    assert response.status_code == 401
    assert result["detail"] == "Not authenticated"


# @pytest.mark.anyio
# async def test_use_inactive_token_headers(
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     dbsession: AsyncSession,
#     user_inactive_token_headers: dict[str, str],
# ) -> None:
#     url = fastapi_app.url_path_for("test_token")
#     response = await client.post(url, headers=user_inactive_token_headers)
#
#     result = response.json()
#     assert response.status_code == 401
#     assert result["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_use_admin_access_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
    superuser_token_headers: dict[str, Any],
) -> None:
    url = fastapi_app.url_path_for("test_admin_token")
    response = await client.post(url, headers=user_token_headers["headers"])

    result = response.json()
    assert response.status_code == 403
    assert result["detail"] == "The user doesn't have enough privileges"

    response_admin = await client.post(url, headers=superuser_token_headers["headers"])
    result = response_admin.json()
    assert response_admin.status_code == 200
    assert result["name"] == "super_admin"
