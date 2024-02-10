import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.dao.user import UserDAO
from app.db.models.user import UserModel
from app.tests.utils.common import (random_lower_string, create_test_user,
                                    get_headers, random_email)


@pytest.mark.anyio
async def test_get_user_models(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests getting a list of users models."""

    dao = UserDAO(dbsession)
    names = ["Bob", "Alan", "Lucy"]
    emails = ["Bob@ya.ru", "Alan@ya.ru", "Lucy@ya.ru"]

    for i in range(3):
        password = random_lower_string()
        await dao.create_user_model(names[i], emails[i], password)

    url = fastapi_app.url_path_for("get_user_models")
    response = await client.get(url)
    users = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(users) == len(names)
    assert all(user['name'] in names for user in users)
    assert all(user['email'] in emails for user in users)


@pytest.mark.anyio
async def test_create_user_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test creating a user model."""
    url = fastapi_app.url_path_for("create_user_model")
    new_user_data = {
        "name": "TestUser",
        "email": "test@example.com",
        "password": "testpassword",
        "is_superuser": False,
        "is_active": True
    }
    response = await client.post(url, json=new_user_data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_user_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test getting a user model by ID."""
    # Create a test user in the database using the DAO
    name = random_lower_string()
    password = random_lower_string()
    email = random_email()
    test_user = await create_test_user(dbsession, name, email, password)

    url = fastapi_app.url_path_for("get_user_model", user_id=test_user.id)
    response = await client.get(url)
    user = response.json()

    assert response.status_code == status.HTTP_200_OK
    # Perform assertions to ensure the retrieved user matches the created user
    assert user["name"] == test_user.name
    assert user["email"] == test_user.email


@pytest.mark.anyio
async def test_get_user_me(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, str]
) -> None:
    name = random_lower_string()
    password = random_lower_string()
    user = await create_test_user(dbsession, name=name, password=password)
    headers = await get_headers(client, fastapi_app, name, password)

    url = fastapi_app.url_path_for("read_user_me")
    response = await client.post(url, headers=headers)

    result = response.json()
    assert response.status_code == 200
    assert result["name"] == user.name
    assert result["email"] == user.email
    assert result["is_superuser"] == user.is_superuser
    assert result["is_active"] == user.is_active
