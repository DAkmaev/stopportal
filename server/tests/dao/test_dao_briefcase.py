from datetime import datetime, timedelta

import pytest
from server.src.db.dao.briefcases import BriefcaseDAO
from server.src.db.models.briefcase import RegistryOperationEnum
from server.tests.utils.common import (
    create_test_briefcase,
    create_test_briefcase_registry,
    create_test_company,
    create_test_user,
    create_test_briefcase_share,
)
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_get_all_briefcases(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)

    user = await create_test_user(dbsession)

    # Get all briefcases
    existing_briefcases = await briefcase_dao.get_all_briefcases(user_id=user.id)
    assert isinstance(existing_briefcases, list)


@pytest.mark.anyio
async def test_get_briefcase_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    FILL_UP = 100
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)

    # Create a briefcase
    await briefcase_dao.create_briefcase_model(fill_up=FILL_UP, user_id=user.id)
    briefcases = await briefcase_dao.get_all_briefcases(user_id=user.id)
    assert len(briefcases) == 1

    # Get a briefcase model by ID
    existing_briefcase = await briefcase_dao.get_briefcase_model(briefcases[0].id)
    assert existing_briefcase is not None
    assert existing_briefcase.id == briefcases[0].id
    assert existing_briefcase.fill_up == briefcases[0].fill_up


@pytest.mark.anyio
async def test_get_briefcase_model_by_user(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    FILL_UP = 100
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)

    # Create a briefcase
    await briefcase_dao.create_briefcase_model(fill_up=FILL_UP, user_id=user.id)
    briefcases = await briefcase_dao.get_all_briefcases(user_id=user.id)
    assert len(briefcases) == 1

    # Get a briefcase model by User
    existing_briefcase = await briefcase_dao.get_briefcase_model_by_user(user)
    assert existing_briefcase is not None
    assert existing_briefcase.id == briefcases[0].id
    assert existing_briefcase.fill_up == briefcases[0].fill_up


@pytest.mark.anyio
async def test_get_all_briefcase_registry(dbsession: AsyncSession) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)

    company1 = await create_test_company(dbsession, user_id=user.id)
    company2 = await create_test_company(dbsession, user_id=user.id)
    briefcase = await create_test_briefcase(dbsession, user_id=user.id)

    # Создаем несколько записей briefcase_registry
    registry1 = await briefcase_dao.create_briefcase_registry_model(
        count=10,
        amount=100.0,
        company_id=company1.id,
        briefcase_id=briefcase.id,
        operation=RegistryOperationEnum.SELL,
    )
    registry2 = await briefcase_dao.create_briefcase_registry_model(
        count=20,
        amount=200.0,
        company_id=company2.id,
        briefcase_id=briefcase.id,
        operation=RegistryOperationEnum.SELL,
    )

    # Получаем все записи briefcase_registry
    briefcase_registry_items = await briefcase_dao.get_all_briefcase_registry(
        briefcase.id
    )

    # Проверяем, что количество записей соответствует ожидаемому
    assert len(briefcase_registry_items) == 2

    # Очищаем тестовые данные

    await briefcase_dao.delete_briefcase_registry_model(registry1.id)
    await briefcase_dao.delete_briefcase_registry_model(registry2.id)


@pytest.mark.anyio
async def test_get_briefcase_registry_by_date_range(dbsession: AsyncSession) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)

    user = await create_test_user(dbsession)
    briefcase = await create_test_briefcase(dbsession, user_id=user.id)
    company = await create_test_company(dbsession, user_id=user.id)

    # Создаем запись briefcase_registry с текущей датой
    registry = await briefcase_dao.create_briefcase_registry_model(
        count=10,
        amount=100.0,
        company_id=company.id,
        briefcase_id=briefcase.id,
        operation=RegistryOperationEnum.SELL,
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
async def test_get_briefcase_registry_model(dbsession: AsyncSession) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)
    registry = await create_test_briefcase_registry(dbsession, user_id=user.id)

    # Получаем запись briefcase_registry по ID
    retrieved_registry = await briefcase_dao.get_briefcase_registry_model(registry.id)

    # Проверяем соответствие полученной записи и исходной
    assert retrieved_registry is not None
    assert retrieved_registry.id == registry.id

    # Очищаем тестовые данные
    await briefcase_dao.delete_briefcase_registry_model(registry.id)


@pytest.mark.anyio
async def test_update_briefcase_registry_model(dbsession: AsyncSession) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)

    registry = await create_test_briefcase_registry(dbsession, user_id=user.id)

    # Обновляем запись briefcase_registry
    updated_fields = {"count": 15, "amount": 150.0}
    updated_registry = await briefcase_dao.update_briefcase_registry_model(
        registry.id, updated_fields
    )

    # Проверяем, что поля были обновлены
    assert updated_registry.count == updated_fields["count"]
    assert updated_registry.amount == updated_fields["amount"]

    # Очищаем тестовые данные
    await briefcase_dao.delete_briefcase_registry_model(registry.id)


@pytest.mark.anyio
async def test_delete_briefcase_registry_model(dbsession: AsyncSession) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)
    registry = await create_test_briefcase_registry(dbsession, user_id=user.id)

    # Удаляем запись briefcase_registry
    await briefcase_dao.delete_briefcase_registry_model(registry.id)
    # Только для закрытия сессии
    await briefcase_dao.get_all_briefcase_registry(registry.briefcase_id)

    # Проверяем, что запись была удалена
    with pytest.raises(HTTPException) as exception:
        await briefcase_dao.get_briefcase_registry_model(registry.id)

    assert exception.value.status_code == 404


@pytest.mark.anyio
async def test_get_all_briefcase_share(dbsession: AsyncSession) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)

    company1 = await create_test_company(dbsession, user_id=user.id)
    company2 = await create_test_company(dbsession, user_id=user.id)
    briefcase = await create_test_briefcase(dbsession, user_id=user.id)

    # Создаем несколько записей briefcase_share
    share1 = await briefcase_dao.create_briefcase_share_model(
        count=100,
        company_id=company1.id,
        briefcase_id=briefcase.id,
    )
    share2 = await briefcase_dao.create_briefcase_share_model(
        count=200,
        company_id=company2.id,
        briefcase_id=briefcase.id,
    )

    # Получаем все записи briefcase_share
    briefcase_shares = await briefcase_dao.get_all_briefcase_shares(briefcase.id)

    # Проверяем, что количество записей соответствует ожидаемому
    assert len(briefcase_shares) == 2
    assert briefcase_shares[0].count == share1.count
    assert briefcase_shares[1].count == share2.count

    # Очищаем тестовые данные
    await briefcase_dao.delete_briefcase_share_model(share1.id)
    await briefcase_dao.delete_briefcase_share_model(share2.id)


@pytest.mark.anyio
async def test_get_briefcase_share_model(dbsession: AsyncSession) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)
    share = await create_test_briefcase_share(dbsession, user_id=user.id)

    # Получаем запись briefcase_share по ID
    retrieved_share = await briefcase_dao.get_briefcase_share_model(share.id)

    # Проверяем соответствие полученной записи и исходной
    assert retrieved_share is not None
    assert retrieved_share.id == share.id

    # Очищаем тестовые данные
    await briefcase_dao.delete_briefcase_share_model(share.id)


@pytest.mark.anyio
async def test_get_briefcase_share_model_by_company(dbsession: AsyncSession) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)

    company1 = await create_test_company(dbsession, user_id=user.id)
    company2 = await create_test_company(dbsession, user_id=user.id)
    briefcase = await create_test_briefcase(dbsession, user_id=user.id)

    share = await create_test_briefcase_share(
        dbsession,
        user_id=user.id,
        briefcase=briefcase,
        company=company1,
    )

    retrieved_share1 = await briefcase_dao.get_briefcase_share_model_by_company(
        briefcase_id=briefcase.id,
        company_id=company1.id,
    )

    assert retrieved_share1 is not None
    assert retrieved_share1.id == share.id

    retrieved_share2 = await briefcase_dao.get_briefcase_share_model_by_company(
        briefcase_id=briefcase.id,
        company_id=company2.id,
    )

    assert retrieved_share2 is None


@pytest.mark.anyio
async def test_update_briefcase_share_model(dbsession: AsyncSession) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)

    share = await create_test_briefcase_share(dbsession, user_id=user.id)

    # Обновляем запись briefcase_share
    updated_fields = {"count": 150}
    updated_share = await briefcase_dao.update_briefcase_share_model(
        share.id, updated_fields
    )

    # Проверяем, что поля были обновлены
    assert updated_share.count == updated_fields["count"]

    # Очищаем тестовые данные
    await briefcase_dao.delete_briefcase_share_model(share.id)


@pytest.mark.anyio
async def test_delete_briefcase_share_model(dbsession: AsyncSession) -> None:
    briefcase_dao = BriefcaseDAO(dbsession)
    user = await create_test_user(dbsession)
    share = await create_test_briefcase_share(dbsession, user_id=user.id)

    # Удаляем запись briefcase_share
    await briefcase_dao.delete_briefcase_share_model(share.id)
    # Только для закрытия сессии
    await briefcase_dao.get_all_briefcase_shares(share.briefcase_id)

    # Проверяем, что запись была удалена
    with pytest.raises(HTTPException) as exception:
        await briefcase_dao.get_briefcase_share_model(share.id)

    assert exception.value.status_code == 404
