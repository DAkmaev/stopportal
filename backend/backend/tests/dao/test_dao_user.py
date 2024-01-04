import pytest
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import verify_password
from backend.db.dao.companies import CompanyDAO
from backend.db.dao.stops import StopsDAO
from backend.db.dao.strategies import StrategiesDAO
from backend.db.dao.user import UserDAO
from backend.tests.utils.common import random_email, random_lower_string


@pytest.mark.anyio
async def test_create_user(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    name = random_lower_string()
    email = random_email()
    password = random_lower_string()

    dao = UserDAO(session=dbsession)

    # Create a new user
    user = await dao.create_user_model(name, email, password)

    assert user.email == email
    assert user.name == name
    assert hasattr(user, "hashed_password")

@pytest.mark.anyio
async def test_authenticate_user(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    name = random_lower_string()
    email = random_email()
    password = random_lower_string()

    dao = UserDAO(session=dbsession)

    # Create a new user
    user = await dao.create_user_model(name, email, password)

    # Указываем правильный пароль
    authenticated_user = await dao.authenticate(name, password)
    assert authenticated_user
    assert user.email == authenticated_user.email

    # Указываем не правильный пароль
    authenticated_user = await dao.authenticate(name, 'wrong')
    assert not authenticated_user


@pytest.mark.anyio
async def test_not_authenticate_user(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    name = random_lower_string()
    password = random_lower_string()

    dao = UserDAO(session=dbsession)

    authenticated_user = await dao.authenticate(name, password)
    assert authenticated_user is None

@pytest.mark.anyio
async def test_update_user(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    name = random_lower_string()
    email = random_email()
    password = random_lower_string()

    dao = UserDAO(session=dbsession)

    # Create a new user
    await dao.create_user_model(name, email, password)
    user = await dao.get_user_by_name(name)


    # Change pwassword and email
    new_password = random_lower_string()
    new_email = random_email()
    update_data = jsonable_encoder(user)
    update_data["password"] = new_password
    update_data["email"] = new_email

    user_updated = await dao.update(user.id, update_data)

    assert user_updated
    assert user.email == user_updated.email
    assert verify_password(new_password, user_updated.hashed_password)

