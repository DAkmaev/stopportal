from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.dao.briefcases import BriefcaseDAO
from backend.db.models.briefcase import RegistryOperationEnum
from backend.tests.utils.common import (create_test_company, create_test_briefcase,
                                        create_test_briefcase_registry)


@pytest.mark.anyio
async def test_create_and_update_briefcase_item_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    COUNT = 10
    DIVIDENDS = 100.0
    NEW_DIVIDENDS = 150.0

    briefcase_dao = BriefcaseDAO(dbsession)

    company = await create_test_company(dbsession, need_add_strategy=True)
    briefcase = await create_test_briefcase(dbsession)

    # Create a briefcase item
    await briefcase_dao.create_briefcase_item_model(
        count=COUNT,
        dividends=DIVIDENDS,
        briefcase_id=briefcase.id,
        company_id=company.id,
        strategy_id=company.strategies[0].id
    )
    briefcase_items = await briefcase_dao.get_all_briefcase_items()
    assert len(briefcase_items) == 1
    new_briefcase_item = briefcase_items[0]
    assert new_briefcase_item is not None
    assert new_briefcase_item.count == COUNT
    assert new_briefcase_item.dividends == DIVIDENDS

    # Update the created briefcase item
    updated_briefcase_item = await briefcase_dao.update_briefcase_item_model(
        briefcase_item_id=new_briefcase_item.id, count=15, dividends=NEW_DIVIDENDS
    )
    assert updated_briefcase_item is not None
    assert updated_briefcase_item.count == 15  # Updated count
    assert updated_briefcase_item.dividends == NEW_DIVIDENDS  # Updated dividends

    # Clean up - delete the test briefcase item
    await briefcase_dao.delete_briefcase_item_model(updated_briefcase_item.id)

    # Ensure the briefcase item has been deleted
    remaining_items = await briefcase_dao.get_all_briefcase_items()
    assert updated_briefcase_item not in remaining_items


@pytest.mark.anyio
async def test_get_all_briefcases(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)

    # Get all briefcases
    existing_briefcases = await briefcase_dao.get_all_briefcases()
    assert isinstance(existing_briefcases, list)


@pytest.mark.anyio
async def test_get_briefcase_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    FILL_UP = 100
    briefcase_dao = BriefcaseDAO(dbsession)

    # Create a briefcase
    await briefcase_dao.create_briefcase_model(FILL_UP)
    briefcases = await briefcase_dao.get_all_briefcases()
    assert len(briefcases) == 1

    # Get a briefcase model by ID
    existing_briefcase = await briefcase_dao.get_briefcase_model(briefcases[0].id)
    assert existing_briefcase is not None
    assert existing_briefcase.id == briefcases[0].id
    assert existing_briefcase.fill_up == briefcases[0].fill_up


@pytest.mark.anyio
async def test_get_briefcase_item_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)

    company = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)
    # Create a briefcase item
    await briefcase_dao.create_briefcase_item_model(
        count=1, dividends=1, company_id=company.id, briefcase_id=briefcase.id
    )
    briefcase_items = await briefcase_dao.get_all_briefcase_items()
    assert len(briefcase_items) == 1

    # Get a briefcase model by ID
    existing_briefcase_item = await briefcase_dao.get_briefcase_item_model(briefcase_items[0].id)
    assert existing_briefcase_item is not None
    assert existing_briefcase_item.id is briefcase_items[0].id

@pytest.mark.anyio
async def test_get_briefcase_items_by_company(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)

    company = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)
    # Create briefcase items for the company
    await briefcase_dao.create_briefcase_item_model(
        count=1, dividends=1, company_id=company.id, briefcase_id=briefcase.id
    )
    await briefcase_dao.create_briefcase_item_model(
        count=2, dividends=2, company_id=company.id, briefcase_id=briefcase.id
    )

    # Get briefcase items for the company
    company_briefcase_items = await briefcase_dao.get_briefcase_items_by_company(company.id)
    assert len(company_briefcase_items) == 2

    # Make sure the retrieved items belong to the correct company
    for item in company_briefcase_items:
        assert item.company_id == company.id


@pytest.mark.anyio
async def test_get_briefcase_items_by_briefcase(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)

    company = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)
    # Create briefcase items for the briefcase
    await briefcase_dao.create_briefcase_item_model(
        count=1, dividends=1, company_id=company.id, briefcase_id=briefcase.id
    )
    await briefcase_dao.create_briefcase_item_model(
        count=2, dividends=2, company_id=company.id, briefcase_id=briefcase.id
    )

    # Get briefcase items for the briefcase
    briefcase_items = await briefcase_dao.get_briefcase_items_by_briefcase(briefcase.id)
    assert len(briefcase_items) == 2

    # Make sure the retrieved items belong to the correct briefcase
    for item in briefcase_items:
        assert item.briefcase_id == briefcase.id


@pytest.mark.anyio
async def test_get_all_briefcase_registry(
    dbsession: AsyncSession
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    company1 = await create_test_company(dbsession)
    company2 = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)

    # Создаем несколько записей briefcase_registry
    registry1 = await briefcase_dao.create_briefcase_registry_model(
        count=10, amount=100.0, company_id=company1.id,
        briefcase_id=briefcase.id, operation=RegistryOperationEnum.SELL
    )
    registry2 = await briefcase_dao.create_briefcase_registry_model(
        count=20, amount=200.0, company_id=company2.id,
        briefcase_id=briefcase.id, operation=RegistryOperationEnum.SELL
    )

    # Получаем все записи briefcase_registry
    briefcase_registry_items = await briefcase_dao.get_all_briefcase_registry(briefcase.id)

    # Проверяем, что количество записей соответствует ожидаемому
    assert len(briefcase_registry_items) == 2

    # Очищаем тестовые данные

    await briefcase_dao.delete_briefcase_registry_model(registry1.id)
    await briefcase_dao.delete_briefcase_registry_model(registry2.id)


@pytest.mark.anyio
async def test_get_briefcase_registry_by_date_range(
    dbsession: AsyncSession
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    briefcase = await create_test_briefcase(dbsession)
    company = await create_test_company(dbsession)

    # Создаем запись briefcase_registry с текущей датой
    registry = await briefcase_dao.create_briefcase_registry_model(
        count=10, amount=100.0, company_id=company.id, briefcase_id=briefcase.id,
        operation=RegistryOperationEnum.SELL
    )

    # фиксируем транзакцию
    await dbsession.flush()

    # Получаем записи briefcase_registry с date range меньше сегодняшней даты
    date_from = datetime.utcnow() - timedelta(days=2)
    date_to = datetime.utcnow() - timedelta(days=1)
    briefcase_registry_items = await briefcase_dao.get_all_briefcase_registry(
        briefcase.id, date_from=date_from, date_to=date_to
    )
    # Проверяем, что нет данных
    assert len(briefcase_registry_items) == 0

    # Получаем записи briefcase_registry с date range больше сегодняшней даты
    date_from = datetime.utcnow() + timedelta(days=1)
    date_to = datetime.utcnow() + timedelta(days=2)
    briefcase_registry_items = await briefcase_dao.get_all_briefcase_registry(
        briefcase.id, date_from=date_from, date_to=date_to
    )
    # Проверяем, что нет данных
    assert len(briefcase_registry_items) == 0

    # Получаем записи briefcase_registry с date range. куда входит наша запись
    date_from = datetime.utcnow() - timedelta(days=1)
    date_to = datetime.utcnow() + timedelta(days=1)
    briefcase_registry_items = await briefcase_dao.get_all_briefcase_registry(
        briefcase.id, date_from=date_from, date_to=date_to
    )
    # Проверяем, что только одна запись соответствует датному диапазону
    assert len(briefcase_registry_items) == 1
    assert briefcase_registry_items[0].id == registry.id

    # Очищаем тестовые данные
    await briefcase_dao.delete_briefcase_registry_model(registry.id)


@pytest.mark.anyio
async def test_get_briefcase_registry_model(
    dbsession: AsyncSession
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    registry = await create_test_briefcase_registry(dbsession)

    # Получаем запись briefcase_registry по ID
    retrieved_registry = await briefcase_dao.get_briefcase_registry_model(registry.id)

    # Проверяем соответствие полученной записи и исходной
    assert retrieved_registry is not None
    assert retrieved_registry.id == registry.id

    # Очищаем тестовые данные
    await briefcase_dao.delete_briefcase_registry_model(registry.id)


@pytest.mark.anyio
async def test_update_briefcase_registry_model(
    dbsession: AsyncSession
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    registry = await create_test_briefcase_registry(dbsession)

    # Обновляем запись briefcase_registry
    updated_fields = {"count": 15, "amount": 150.0}
    updated_registry = await briefcase_dao.update_briefcase_registry_model(registry.id, updated_fields)

    # Проверяем, что поля были обновлены
    assert updated_registry.count == updated_fields["count"]
    assert updated_registry.amount == updated_fields["amount"]

    # Очищаем тестовые данные
    await briefcase_dao.delete_briefcase_registry_model(registry.id)


@pytest.mark.anyio
async def test_delete_briefcase_registry_model(
    dbsession: AsyncSession
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    registry = await create_test_briefcase_registry(dbsession)

    # Удаляем запись briefcase_registry
    await briefcase_dao.delete_briefcase_registry_model(registry.id)
    # Только для закрытия сессии
    await briefcase_dao.get_all_briefcase_registry(registry.briefcase_id)

    # Проверяем, что запись была удалена
    with pytest.raises(HTTPException) as exception:
        await briefcase_dao.get_briefcase_registry_model(registry.id)

    assert exception.value.status_code == 404
