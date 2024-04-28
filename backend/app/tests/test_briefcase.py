from datetime import datetime
from typing import Any

import pytest
from app.db.dao.briefcases import BriefcaseDAO
from app.db.models.briefcase import CurrencyEnum, RegistryOperationEnum
from app.tests.utils.common import (
    create_test_briefcase,
    create_test_briefcase_registry,
    create_test_company,
)
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_create_briefcase_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()

    url = fastapi_app.url_path_for("create_briefcase_model")
    fill_up = 100.0
    response = await client.post(
        url,
        json={
            "fill_up": fill_up,
        },
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    dao = BriefcaseDAO(dbsession)
    instances = await dao.get_all_briefcases(user_id=user.id)
    assert instances[0].fill_up == fill_up


@pytest.mark.anyio
async def test_get_briefcase(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()

    # Create a test briefcase in the database
    fill_up = 100
    briefcase = await create_test_briefcase(dbsession, user_id=user.id, fill_up=fill_up)

    # Test retrieving the created item
    url = fastapi_app.url_path_for("get_briefcase_model", briefcase_id=briefcase.id)

    response = await client.get(url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == briefcase.id
    assert data["fill_up"] == briefcase.fill_up


@pytest.mark.anyio
async def test_create_briefcase_registry_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Test creating a briefcase registry model."""
    count = 5
    amount = 1
    price = 100.0

    user, headers = user_token_headers.values()
    company = await create_test_company(dbsession, user_id=user.id)
    briefcase = await create_test_briefcase(dbsession, user_id=user.id)

    url = fastapi_app.url_path_for(
        "create_briefcase_registry_model", briefcase_id=briefcase.id
    )

    # Проверяем с передачей стратегии
    response = await client.post(
        url,
        json={
            "count": count,
            "amount": amount,
            "price": price,
            "company": {"id": company.id},
            "briefcase": {"id": briefcase.id},
            "operation": RegistryOperationEnum.BUY.value,
            "currency": CurrencyEnum.RUB.value,
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    dao = BriefcaseDAO(dbsession)
    instances = await dao.get_all_briefcase_registry(briefcase.id)
    assert instances[0].count == count
    assert instances[0].amount == amount
    assert instances[0].price == price
    assert instances[0].company_id == company.id
    assert instances[0].briefcase_id == briefcase.id
    assert instances[0].operation == RegistryOperationEnum.BUY
    assert instances[0].currency == CurrencyEnum.RUB


@pytest.mark.anyio
async def test_get_briefcase_registry(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Test getting a briefcase registry."""

    user, headers = user_token_headers.values()

    # Create a test registry in the database
    test_registry = await create_test_briefcase_registry(dbsession, user_id=user.id)

    # Test retrieving the created registry
    url = fastapi_app.url_path_for(
        "get_briefcase_registry",
        briefcase_id=test_registry.briefcase_id,
        item_id=test_registry.id,
    )

    response = await client.get(url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_registry.id


@pytest.mark.anyio
async def test_get_briefcase_registries(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Test getting all registries in a briefcase."""

    user, headers = user_token_headers.values()

    # Create test registry in the database
    company = await create_test_company(dbsession, user_id=user.id)
    briefcase = await create_test_briefcase(dbsession, user_id=user.id)
    registry1 = await create_test_briefcase_registry(
        dbsession, user_id=user.id, briefcase=briefcase, company=company
    )
    registry2 = await create_test_briefcase_registry(
        dbsession, user_id=user.id, briefcase=briefcase, company=company
    )

    # Test retrieving all registries
    url = fastapi_app.url_path_for(
        "get_briefcase_registries", briefcase_id=briefcase.id
    )
    response = await client.get(url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == registry1.id
    assert data[1]["id"] == registry2.id


@pytest.mark.anyio
async def test_update_briefcase_registry(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Test updating a briefcase registry."""

    user, headers = user_token_headers.values()

    # Create a test registry in the database
    test_registry = await create_test_briefcase_registry(dbsession, user_id=user.id)

    # Update data for the registry
    updated_count = 20
    updated_amount = 2000.0
    operation = RegistryOperationEnum.SELL
    currency = CurrencyEnum.USD

    # Test updating the registry
    url = fastapi_app.url_path_for(
        "update_briefcase_registry",
        briefcase_id=test_registry.briefcase_id,
        item_id=test_registry.id,
    )
    response = await client.put(
        url,
        json={
            "count": updated_count,
            "amount": updated_amount,
            "company": {"id": test_registry.company.id},
            "briefcase": {"id": test_registry.briefcase.id},
            "operation": operation.value,
            "currency": currency.value,
            "created_date": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK

    # Check if the registry was updated in the database
    dao = BriefcaseDAO(dbsession)
    updated_registry = await dao.get_briefcase_registry_model(test_registry.id)
    assert updated_registry.count == updated_count
    assert updated_registry.amount == updated_amount
    assert updated_registry.operation == operation
    assert updated_registry.currency == currency


@pytest.mark.anyio
async def test_delete_briefcase_registry(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Test deleting a briefcase registry."""

    user, headers = user_token_headers.values()

    # Create a test registry in the database
    test_registry = await create_test_briefcase_registry(dbsession, user_id=user.id)

    # Test deleting the registry
    url = fastapi_app.url_path_for(
        "delete_briefcase_registry",
        briefcase_id=test_registry.briefcase_id,
        item_id=test_registry.id,
    )

    response = await client.delete(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check if the registry was deleted from the database
    dao = BriefcaseDAO(dbsession)
    instances = await dao.get_all_briefcase_registry(test_registry.briefcase_id)
    assert len(instances) == 0
