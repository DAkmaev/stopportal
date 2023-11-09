import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.db.dao.strategies import StrategiesDAO


@pytest.mark.anyio
async def test_get_strategy_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests getting a strategy model by ID."""
    # Создаем стратегию для получения
    strategy_name = "Test Strategy"
    strategy_description = "Test description"

    strategies_dao = StrategiesDAO(dbsession)
    await strategies_dao.create_strategy_model(
        name=strategy_name,
        description=strategy_description
    )

    # Получаем созданную стратегию
    created_strategy = await strategies_dao.get_strategy_model_by_name(strategy_name)
    assert created_strategy is not None


    # Отправляем GET-запрос для получения стратегии по ID
    url = fastapi_app.url_path_for("get_strategy_model", strategy_id=created_strategy.id)
    response = await client.get(url)
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
) -> None:
    """Tests getting a list of strategy models."""
    # Создаем несколько стратегий в базе данных
    strategies_dao = StrategiesDAO(dbsession)
    strategy_names = ["Strategy 1", "Strategy 2", "Strategy 3"]

    for name in strategy_names:
        await strategies_dao.create_strategy_model(name=name, description=f"{name} description")

    # Отправляем GET-запрос для получения списка стратегий
    url = fastapi_app.url_path_for("get_strategy_models")
    response = await client.get(url)
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
) -> None:
    """Tests creating a new strategy model."""
    # Генерируем уникальное имя для стратегии
    strategy_name = uuid.uuid4().hex

    # Отправляем POST-запрос для создания новой стратегии
    url = fastapi_app.url_path_for("create_strategy_model")
    response = await client.post(
        url,
        json={
            "name": strategy_name,
            "description": "Test description",
        },
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
) -> None:
    """Tests updating a strategy model."""
    # Создаем стратегию для обновления
    original_name = "Original Strategy"
    original_description = "Original description"
    updated_name = "Updated Strategy"
    updated_description = "Updated description"

    strategies_dao = StrategiesDAO(dbsession)
    original_strategy = await strategies_dao.create_strategy_model(
        name=original_name,
        description=original_description
    )

    # Получаем созданную стратегию
    strategy = await strategies_dao.get_strategy_model_by_name(original_name)
    assert strategy is not None

    # Отправляем PUT-запрос для обновления стратегии
    url = fastapi_app.url_path_for("update_strategy_model", id=original_strategy.id)
    response = await client.put(
        url,
        json={
            "name": updated_name,
            "description": updated_description,
        },
    )

    # Проверяем успешный ответ и обновление стратегии в базе данных
    assert response.status_code == status.HTTP_200_OK
    updated_strategy = await strategies_dao.get_strategy_model(original_strategy.id)
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
) -> None:
    """Tests deleting a strategy model."""
    # Создаем стратегию для удаления
    strategy_name = "Test Strategy"
    strategy_description = "Test description"

    strategies_dao = StrategiesDAO(dbsession)
    await strategies_dao.create_strategy_model(
        name=strategy_name,
        description=strategy_description
    )

    # Получаем созданную стратегию
    strategy = await strategies_dao.get_strategy_model_by_name(strategy_name)
    assert strategy is not None

    # Отправляем DELETE-запрос для удаления стратегии
    url = fastapi_app.url_path_for("delete_strategy_model", id=strategy.id)
    response = await client.delete(url)

    # Проверяем успешный ответ и отсутствие удаленной стратегии в базе данных
    assert response.status_code == status.HTTP_204_NO_CONTENT
    deleted_strategy = await strategies_dao.get_strategy_model_by_name(strategy_name)

    assert deleted_strategy is None
