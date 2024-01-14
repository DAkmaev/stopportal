from datetime import datetime

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dao.briefcases import BriefcaseDAO
from backend.db.models.briefcase import RegistryOperationEnum, CurrencyEnum
from backend.tests.utils.common import (create_test_company, create_test_briefcase_item,
                                        create_test_briefcase,
                                        create_test_briefcase_registry)


@pytest.mark.anyio
async def test_create_briefcase_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test creating a briefcase model."""
    url = fastapi_app.url_path_for("create_briefcase_model")
    fill_up = 100.0
    response = await client.post(
        url,
        json={
            "fill_up": fill_up,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    dao = BriefcaseDAO(dbsession)
    instances = await dao.get_all_briefcases()
    assert instances[0].fill_up == fill_up


@pytest.mark.anyio
async def test_create_briefcase_item_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test creating a briefcase item model."""
    count = 5
    dividends = 50.0
    briefcase_id = 1
    url = fastapi_app.url_path_for("create_briefcase_item_model", briefcase_id=briefcase_id)

    company = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)

    # Проверяем с передачей стратегии
    response = await client.post(
        url,
        json={
            "count": count,
            "dividends": dividends,
            "company": {"id": company.id},
            "strategy": {"id": 1},
            "briefcase_id": briefcase.id
        },
    )

    assert response.status_code == status.HTTP_200_OK
    dao = BriefcaseDAO(dbsession)
    instances = await dao.get_all_briefcase_items()
    assert instances[0].count == count
    assert instances[0].dividends == dividends


@pytest.mark.anyio
async def test_create_briefcase_item_model_no_strategy(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test creating a briefcase item model."""
    count = 5
    dividends = 50.0
    briefcase_id = 1

    company = await create_test_company(dbsession, False, True)
    briefcase = await create_test_briefcase(dbsession)

    url = fastapi_app.url_path_for("create_briefcase_item_model",
                                   briefcase_id=briefcase.id)

    # Проверяем с пустой стратегией
    response = await client.post(
        url,
        json={
            "count": count,
            "dividends": dividends,
            "company": {"id": company.id},
            "briefcase_id": briefcase.id
        },
    )
    assert response.status_code == status.HTTP_200_OK
    dao = BriefcaseDAO(dbsession)
    instances = await dao.get_all_briefcase_items()
    assert instances[0].count == count
    assert instances[0].dividends == dividends


@pytest.mark.anyio
async def test_create_briefcase_item_model_wrong_company(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test creating a briefcase item model."""
    count = 5
    dividends = 50.0
    briefcase_id = 1
    url = fastapi_app.url_path_for("create_briefcase_item_model", briefcase_id=briefcase_id)

    briefcase = await create_test_briefcase(dbsession)

    # Проверяем с несуществующей компанией
    response = await client.post(
        url,
        json={
            "count": count,
            "dividends": dividends,
            "company": {"id": 1000},
            "briefcase_id": briefcase.id
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    dao = BriefcaseDAO(dbsession)
    instances = await dao.get_all_briefcase_items()
    assert len(instances) == 0


@pytest.mark.anyio
async def test_get_briefcase_item(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test getting a briefcase item."""
    # Create a test item in the database
    test_item = await create_test_briefcase_item(dbsession)

    # Test retrieving the created item
    url = fastapi_app.url_path_for("get_briefcase_item",
                                   item_id=test_item.id)

    response = await client.get(url)
    print(response)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_item.id


@pytest.mark.anyio
async def test_get_briefcase_items(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test getting all items in a briefcase."""
    # Create test item in the database
    await create_test_briefcase_item(dbsession)

    # Test retrieving all items
    briefcase_id = 1  # Assuming a specific briefcase ID
    url = fastapi_app.url_path_for("get_briefcase_items",
                                   briefcase_id=briefcase_id)
    response = await client.get(url)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0  # Check if there's at least one item returned


@pytest.mark.anyio
async def test_update_briefcase_item(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test updating a briefcase item."""
    # Create a test item in the database
    test_item = await create_test_briefcase_item(dbsession)

    # Update data for the item
    updated_count = 10
    updated_dividends = 100.0

    # Test updating the item
    url = fastapi_app.url_path_for("update_briefcase_item", item_id=test_item.id)
    response = await client.put(
        url,
        json={
            "count": updated_count,
            "dividends": updated_dividends,
            "company": {"id": test_item.company_id},
            "briefcase_id": test_item.briefcase_id
        },
    )

    assert response.status_code == status.HTTP_200_OK

    # Check if the item was updated in the database
    dao = BriefcaseDAO(dbsession)
    updated_item = await dao.get_briefcase_item_model(test_item.id)
    assert updated_item.count == updated_count
    assert updated_item.dividends == updated_dividends


@pytest.mark.anyio
async def test_delete_briefcase_item(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test deleting a briefcase item."""
    # Create a test item in the database
    test_item = await create_test_briefcase_item(dbsession)

    # Test deleting the item
    url = fastapi_app.url_path_for("delete_briefcase_item", item_id=test_item.id)

    response = await client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check if the item was deleted from the database
    dao = BriefcaseDAO(dbsession)
    instances = await dao.get_all_briefcase_items()
    assert len(instances) == 0


#######################################################################
@pytest.mark.anyio
async def test_create_briefcase_registry_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test creating a briefcase registry model."""
    count = 5
    amount = 1
    price = 100.0

    company = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)

    url = fastapi_app.url_path_for("create_briefcase_registry_model",
                                   briefcase_id=briefcase.id)

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
) -> None:
    """Test getting a briefcase registry."""
    # Create a test registry in the database
    test_registry = await create_test_briefcase_registry(dbsession)

    # Test retrieving the created registry
    url = fastapi_app.url_path_for("get_briefcase_registry",
                                   item_id=test_registry.id)

    response = await client.get(url)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_registry.id


@pytest.mark.anyio
async def test_get_briefcase_registries(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test getting all registries in a briefcase."""
    # Create test registry in the database
    company = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)
    registry1 = await create_test_briefcase_registry(dbsession, briefcase, company)
    registry2 = await create_test_briefcase_registry(dbsession, briefcase, company)

    # Test retrieving all registries
    url = fastapi_app.url_path_for("get_briefcase_registries",
                                   briefcase_id=briefcase.id)
    response = await client.get(url)

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
) -> None:
    """Test updating a briefcase registry."""
    # Create a test registry in the database
    test_registry = await create_test_briefcase_registry(dbsession)

    # Update data for the registry
    updated_count = 10
    updated_amount = 100.0
    operation = RegistryOperationEnum.SELL
    currency = CurrencyEnum.USD

    # Test updating the registry
    url = fastapi_app.url_path_for("update_briefcase_registry", item_id=test_registry.id)
    response = await client.put(
        url,
        json={
            "count": updated_count,
            "amount": updated_amount,
            "company": {"id": test_registry.company.id},
            "briefcase": {"id": test_registry.briefcase.id},
            "operation": operation.value,
            "currency": currency.value,
            "created_date": datetime.now().isoformat()
        }
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
) -> None:
    """Test deleting a briefcase registry."""
    # Create a test registry in the database
    test_registry = await create_test_briefcase_registry(dbsession)

    # Test deleting the registry
    url = fastapi_app.url_path_for("delete_briefcase_registry", item_id=test_registry.id)

    response = await client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check if the registry was deleted from the database
    dao = BriefcaseDAO(dbsession)
    instances = await dao.get_all_briefcase_registry(test_registry.briefcase_id)
    assert len(instances) == 0
