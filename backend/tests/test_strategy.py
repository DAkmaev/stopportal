import uuid
from typing import Any

import pytest
from backend.app.db.dao.companies import CompanyDAO
from backend.app.db.dao.strategies import StrategiesDAO
from backend.tests.utils.common import get_user_token_headers
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


@pytest.mark.anyio
async def test_get_strategy_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Tests getting a strategy model by ID."""
    user, headers = user_token_headers.values()

    # Создаем стратегию для получения
    strategy_name = "Test Strategy"
    strategy_description = "Test description"

    strategies_dao = StrategiesDAO(dbsession)
    await strategies_dao.create_strategy_model(
        name=strategy_name, description=strategy_description, user_id=user.id
    )

    # Получаем созданную стратегию
    created_strategy = await strategies_dao.get_strategy_model_by_name(strategy_name)
    assert created_strategy is not None

    # Отправляем GET-запрос для получения стратегии по ID
    url = fastapi_app.url_path_for("get_strategy", strategy_id=created_strategy.id)
    response = await client.get(url, headers=headers)
    retrieved_strategy = response.json()

    # Проверяем успешный ответ и соответствие данных полученным из базы
    assert response.status_code == status.HTTP_200_OK
    assert retrieved_strategy["id"] == created_strategy.id
    assert retrieved_strategy["name"] == strategy_name
    assert retrieved_strategy["description"] == strategy_description


@pytest.mark.anyio
async def test_get_strategy_models(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Tests getting a list of strategy models."""
    user, headers = user_token_headers.values()

    # Создаем несколько стратегий в базе данных
    strategies_dao = StrategiesDAO(dbsession)
    strategy_names = ["Strategy 1", "Strategy 2", "Strategy 3"]

    for name in strategy_names:
        await strategies_dao.create_strategy_model(
            name=name, description=f"{name} description", user_id=user.id
        )

    # Отправляем GET-запрос для получения списка стратегий
    url = fastapi_app.url_path_for("get_strategies")
    response = await client.get(url, headers=headers)
    strategies = response.json()

    # Проверяем успешный ответ и соответствие данных полученным из базы
    assert response.status_code == status.HTTP_200_OK
    assert len(strategies) == len(strategy_names)
    assert all(strategy["name"] in strategy_names for strategy in strategies)


@pytest.mark.anyio
async def test_create_strategy_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Tests creating a new strategy model."""

    # Генерируем уникальное имя для стратегии
    strategy_name = uuid.uuid4().hex

    # Отправляем POST-запрос для создания новой стратегии
    url = fastapi_app.url_path_for("create_strategy")
    response = await client.post(
        url,
        json={
            "name": strategy_name,
            "description": "Test description",
        },
        headers=user_token_headers["headers"],
    )

    # Проверяем успешный ответ и наличие созданной стратегии в базе данных
    assert response.status_code == status.HTTP_200_OK

    dao = StrategiesDAO(dbsession)
    created_strategy = await dao.get_strategy_model_by_name(strategy_name)
    assert created_strategy is not None
    assert created_strategy.name == strategy_name

    # Удаляем созданную стратегию после теста
    await dao.delete_strategy_model(created_strategy.id)


@pytest.mark.anyio
async def test_update_strategy_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Tests updating a strategy model."""
    user, headers = user_token_headers.values()

    # Создаем стратегию для обновления
    original_name = "Original Strategy"
    original_description = "Original description"
    updated_name = "Updated Strategy"
    updated_description = "Updated description"

    # Отправляем POST-запрос для создания новой стратегии
    url = fastapi_app.url_path_for("create_strategy")
    original_response = await client.post(
        url,
        json={
            "name": original_name,
            "description": original_description,
        },
        headers=user_token_headers["headers"],
    )
    strategy_id = original_response.json()["user_id"]

    # Отправляем PUT-запрос для обновления стратегии
    url = fastapi_app.url_path_for(
        "update_strategy",
        strategy_id=strategy_id,
    )
    response = await client.put(
        url,
        json={
            "name": updated_name,
            "description": updated_description,
        },
        headers=user_token_headers["headers"],
    )
    assert response.status_code == status.HTTP_200_OK

    # Проверяем успешный ответ и обновление стратегии в базе данных
    strategies_dao = StrategiesDAO(dbsession)
    updated_strategy = await strategies_dao.get_strategy_model(strategy_id)
    assert updated_strategy is not None
    assert updated_strategy.name == updated_name
    assert updated_strategy.description == updated_description

    # Удаляем созданную стратегию после теста
    await strategies_dao.delete_strategy_model(updated_strategy.id)


@pytest.mark.anyio
async def test_delete_strategy_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Tests deleting a strategy model."""
    # Создаем стратегию для удаления
    strategy_name = "Test Strategy"
    strategy_description = "Test description"

    # Отправляем POST-запрос для создания новой стратегии
    url = fastapi_app.url_path_for("create_strategy")
    response = await client.post(
        url,
        json={
            "name": strategy_name,
            "description": strategy_description,
        },
        headers=user_token_headers["headers"],
    )
    strategy_id = response.json()["user_id"]

    # Отправляем DELETE-запрос для удаления стратегии
    url = fastapi_app.url_path_for("delete_strategy", strategy_id=strategy_id)
    response = await client.delete(
        url,
        headers=user_token_headers["headers"],
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Проверяем успешный ответ и отсутствие удаленной стратегии в базе данных
    strategies_dao = StrategiesDAO(dbsession)
    deleted_strategy = await strategies_dao.get_strategy_model_by_name(strategy_name)

    assert deleted_strategy is None


@pytest.mark.anyio
async def test_update_strategies_in_company(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Tests updating strategies in a company."""
    user, headers = user_token_headers.values()

    # Создаем компанию и несколько стратегий для обновления списка
    company_name = "Test Company"
    company_ticker = "TIKER"
    company_type = "MOEX"
    strategy_names = ["Strategy 1", "Strategy 2", "Strategy 3"]
    company_dao = CompanyDAO(dbsession)
    strategies_dao = StrategiesDAO(dbsession)

    await company_dao.create_company_model(
        name=company_name,
        tiker=company_ticker,
        company_type=company_type,
        user_id=user.id,
    )

    url = fastapi_app.url_path_for("create_strategy")
    for strategy_name in strategy_names:
        await client.post(
            url,
            json={
                "name": strategy_name,
                "description": f"{strategy_name} description",
            },
            headers=headers,
        )

    # Получаем созданную компанию и стратегии
    retrieved_company = await company_dao.get_company_model_by_tiker(
        company_ticker, user.id
    )
    retrieved_strategies = []
    for strategy_name in strategy_names:
        strategy = await strategies_dao.get_strategy_model_by_name(strategy_name)
        retrieved_strategies.append(strategy)

    assert retrieved_company is not None
    assert all(strategy is not None for strategy in retrieved_strategies)

    # Отправляем PATCH-запрос для обновления списка стратегий у компании
    url = fastapi_app.url_path_for(
        "partial_update_company", company_id=retrieved_company.id
    )
    response = await client.patch(
        url,
        json={
            "strategies": [
                {"id": retrieved_strategies[0].id},
                {"id": retrieved_strategies[1].id},
                {"id": retrieved_strategies[2].id},
            ]
        },
        headers=headers,
    )

    # Проверяем успешный ответ и обновление списка стратегий компании в базе данных
    assert response.status_code == status.HTTP_200_OK
    updated_company = await company_dao.get_company_model(retrieved_company.id)
    assert updated_company is not None
    assert len(updated_company.strategies) == 3

    # Пробуем оставить одну стратегию
    # Отправляем PATCH-запрос для обновления списка стратегий у компании
    url = fastapi_app.url_path_for(
        "partial_update_company", company_id=retrieved_company.id
    )
    response = await client.patch(
        url,
        json={"strategies": [{"id": retrieved_strategies[1].id}]},
        headers=headers,
    )

    # Проверяем успешный ответ и обновление списка стратегий компании в базе данных
    assert response.status_code == status.HTTP_200_OK
    updated_company = await company_dao.get_company_model(retrieved_company.id)
    assert len(updated_company.strategies) == 1
    assert updated_company.strategies[0].name == strategy_names[1]

    # Пробуем удалить все стратегии
    # Отправляем PATCH-запрос для обновления списка стратегий у компании
    url = fastapi_app.url_path_for(
        "partial_update_company", company_id=retrieved_company.id
    )
    response = await client.patch(
        url,
        json={"strategies": []},
        headers=headers,
    )

    # Проверяем успешный ответ и обновление списка стратегий компании в базе данных
    assert response.status_code == status.HTTP_200_OK
    updated_company = await company_dao.get_company_model(retrieved_company.id)
    assert len(updated_company.strategies) == 0

    # Удаляем созданные компанию и стратегии после теста
    await company_dao.delete_company_model(updated_company.id)
    for strategy in retrieved_strategies:
        await strategies_dao.delete_strategy_model(strategy.id)


@pytest.mark.anyio
async def test_check_permissions_delete_strategy_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests deleting a strategy model."""

    # Создаем стратегию для удаления
    strategy_name = "Test Strategy"
    strategy_description = "Test description"

    original_user_date = await get_user_token_headers(client, fastapi_app, dbsession)
    new_user_data = await get_user_token_headers(client, fastapi_app, dbsession)

    user_original = original_user_date["user"]
    user_new_headers = new_user_data["headers"]

    strategy_dao = StrategiesDAO(dbsession)
    await strategy_dao.create_strategy_model(
        name=strategy_name, description=strategy_description, user_id=user_original.id
    )
    strategy = await strategy_dao.get_strategy_model_by_name(strategy_name)

    # Отправляем DELETE-запрос для удаления стратегии
    url = fastapi_app.url_path_for("delete_strategy", strategy_id=strategy.id)
    response = await client.delete(
        url,
        headers=user_new_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Проверяем, что стратегия не исчезла
    deleted_strategy = await strategy_dao.get_strategy_model(strategy.id)

    assert deleted_strategy == strategy
