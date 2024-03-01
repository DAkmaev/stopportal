import uuid
from typing import Any

import pytest
from app.db.dao.companies import CompanyDAO
from app.db.dao.stops import StopsDAO
from app.db.models.company import CompanyModel, StopModel
from app.tests.utils.common import create_test_company, create_test_user, get_headers
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


@pytest.mark.anyio
async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Tests company instance creation."""
    url = fastapi_app.url_path_for("create_company_model")
    tiker_name = uuid.uuid4().hex
    response = await client.post(
        url,
        json={
            "tiker": tiker_name,
        },
        headers=user_token_headers['headers'],
    )
    assert response.status_code == status.HTTP_200_OK
    dao = CompanyDAO(dbsession)
    instances = await dao.filter(tiker=tiker_name)
    assert instances[0].tiker == tiker_name


@pytest.mark.anyio
async def test_get_company_by_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test retrieving a company by ID."""
    user_password = 'password'
    user_name = 'test_user'
    user = await create_test_user(dbsession, name=user_name, password=user_password)
    user_token_headers = await get_headers(client, fastapi_app, user_name, user_password)

    # Создаем тестовую компанию в базе данных
    company = await create_test_company(dbsession, True, True, user_id=user.id)

    # Отправляем GET-запрос
    url = fastapi_app.url_path_for("get_company_model", company_id=company.id)
    response = await client.get(url, headers=user_token_headers)

    # Проверяем успешный ответ и соответствие данных полученным из базы
    assert response.status_code == status.HTTP_200_OK
    company_response = response.json()
    assert company_response["tiker"] == company.tiker
    assert company_response["name"] == company.name
    assert len(company_response["stops"]) == 2
    assert company_response["stops"][0]["value"] == company.stops[0].value
    assert len(company_response["strategies"]) == 2


@pytest.mark.anyio
async def test_getting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests company instance retrieval."""
    user_password = 'password'
    user_name = 'test_user'
    user = await create_test_user(dbsession, name=user_name, password=user_password)
    user_token_headers = await get_headers(client, fastapi_app, user_name,
                                           user_password)

    company = await create_test_company(dbsession, True, True, user_id=user.id)

    url = fastapi_app.url_path_for("get_company_models")
    response = await client.get(url, headers=user_token_headers)
    companies = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(companies) == 1
    assert companies[0]["tiker"] == company.tiker
    assert companies[0]["name"] == company.name
    assert len(companies[0]["stops"]) == 2
    assert companies[0]["stops"][0]["value"] == company.stops[0].value
    assert len(companies[0]["strategies"]) == 2


@pytest.mark.anyio
async def test_updating(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests company instance updating."""

    user_password = 'password'
    user_name = 'test_user'
    user = await create_test_user(dbsession, name=user_name, password=user_password)
    user_token_headers = await get_headers(client, fastapi_app, user_name,
                                           user_password)

    company = await create_test_company(dbsession, True, True, user_id=user.id)
    assert len(company.stops) == 2
    assert len(company.strategies) == 2

    url = fastapi_app.url_path_for("update_company_model", company_id=company.id)
    response = await client.put(
        url,
        json={
            "tiker": "LKOH",
            "name": "Лукойл",
            "type": "MOEX",
            "strategies": [{"id": 1}],
        },
        headers=user_token_headers,
    )

    dao = CompanyDAO(dbsession)
    updated_company = await dao.get_company_model(company.id)

    assert response.status_code == status.HTTP_200_OK
    assert updated_company.tiker == company.tiker
    assert updated_company.name == company.name
    assert len(updated_company.stops) == 2
    assert len(updated_company.strategies) == 1
