import pytest
from server.src.db.dao.strategies import StrategiesDAO
from server.tests.utils.common import create_test_user
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_add_strategy_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    NAME = "Test Strategy"
    DESCRIPTION = "Test description"

    strategies_dao = StrategiesDAO(dbsession)

    user = await create_test_user(dbsession)
    # Create a new strategy
    await strategies_dao.create_strategy_model(
        name=NAME, description=DESCRIPTION, user_id=user.id
    )

    # Retrieve the created strategy
    strategy = await strategies_dao.get_strategy_model_by_name(NAME)
    assert strategy is not None
    assert strategy.description == DESCRIPTION
    assert strategy.name == NAME
    assert strategy.user == user

    await strategies_dao.delete_strategy_model(strategy.id)


@pytest.mark.anyio
async def test_get_strategy_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    # Создаем стратегию для получения
    strategy_name = "Test Strategy"
    strategy_description = "Test description"

    strategies_dao = StrategiesDAO(dbsession)
    user = await create_test_user(dbsession)
    created_strategy = await strategies_dao.create_strategy_model(
        name=strategy_name, description=strategy_description, user_id=user.id
    )

    # Retrieve the created strategy
    strategy = await strategies_dao.get_strategy_model_by_name(strategy_name)
    assert strategy is not None

    # Получаем стратегию по идентификатору
    retrieved_strategy = await strategies_dao.get_strategy_model(
        strategy_id=created_strategy.id
    )

    # Проверяем, что стратегия была успешно получена и имеет правильные параметры
    assert retrieved_strategy is not None
    assert retrieved_strategy.id == created_strategy.id
    assert retrieved_strategy.name == strategy_name
    assert retrieved_strategy.description == strategy_description
    assert retrieved_strategy.user == user

    await strategies_dao.delete_strategy_model(created_strategy.id)


@pytest.mark.anyio
async def test_get_strategies_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    # Создаем стратегию для получения
    strategy_name = "Test Strategy"
    strategy_description = "Test description"
    user = await create_test_user(dbsession)

    strategies_dao = StrategiesDAO(dbsession)
    await strategies_dao.create_strategy_model(
        name=strategy_name, description=strategy_description, user_id=user.id
    )

    # Получаем стратегию по идентификатору
    retrieved_strategies = await strategies_dao.get_all_strategies_model(
        user_id=user.id
    )

    # Проверяем, что стратегия была успешно получена и имеет правильные параметры
    assert retrieved_strategies is not None
    assert len(retrieved_strategies) == 1
    assert retrieved_strategies[0].name == strategy_name
    assert retrieved_strategies[0].description == strategy_description
    assert retrieved_strategies[0].user == user

    await strategies_dao.delete_strategy_model(retrieved_strategies[0].id)


@pytest.mark.anyio
async def test_get_strategy_model_by_name(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    NAME = "Test Strategy"
    DESCRIPTION = "Test description"

    strategies_dao = StrategiesDAO(dbsession)
    user = await create_test_user(dbsession)

    # Create a new strategy
    await strategies_dao.create_strategy_model(
        name=NAME, description=DESCRIPTION, user_id=user.id
    )

    # Retrieve the created strategy
    strategy = await strategies_dao.get_strategy_model_by_name(NAME)
    assert strategy is not None

    # Retrieve the created strategy by name
    strategy = await strategies_dao.get_strategy_model_by_name(NAME)

    # Check that the retrieved strategy matches the created one
    assert strategy is not None
    assert strategy.description == DESCRIPTION
    assert strategy.name == NAME
    assert strategy.user == user

    await strategies_dao.delete_strategy_model(strategy.id)


@pytest.mark.anyio
async def test_get_all_strategies_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    # Создаем несколько стратегий
    strategies_dao = StrategiesDAO(dbsession)
    strategy_names = ["Strategy 1", "Strategy 2", "Strategy 3"]
    strategy_descriptions = ["Description 1", "Description 2", "Description 3"]
    user = await create_test_user(dbsession)

    for name, description in zip(strategy_names, strategy_descriptions):
        await strategies_dao.create_strategy_model(
            name=name, description=description, user_id=user.id
        )

    # Получаем все стратегии
    retrieved_strategies = await strategies_dao.get_all_strategies_model(
        user_id=user.id
    )

    # Проверяем, что количество полученных стратегий соответствует ограничению
    assert len(retrieved_strategies) == len(strategy_names)

    # Проверяем, что данные стратегий соответствуют ожидаемым
    for index, strategy in enumerate(retrieved_strategies):
        expected_name = strategy_names[index]
        expected_description = strategy_descriptions[index]

        assert strategy.name == expected_name
        assert strategy.description == expected_description
        assert strategy.user == user


@pytest.mark.anyio
async def test_delete_strategy_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    NAME = "Test Strategy"
    DESCRIPTION = "Test description"

    strategies_dao = StrategiesDAO(dbsession)
    user = await create_test_user(dbsession)

    # Create a new strategy
    strategy = await strategies_dao.create_strategy_model(
        name=NAME, description=DESCRIPTION, user_id=user.id
    )

    # Retrieve the created strategy
    strategy = await strategies_dao.get_strategy_model_by_name(NAME)
    assert strategy is not None

    # Delete the created strategy
    await strategies_dao.delete_strategy_model(strategy.id)

    # Attempt to retrieve the deleted strategy and ensure it doesn't exist
    deleted_strategy = await strategies_dao.get_strategy_model_by_name(NAME)
    assert deleted_strategy is None


@pytest.mark.anyio
async def test_update_strategy_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    # Создаем стратегию для редактирования
    original_name = "Original Strategy"
    original_description = "Original description"
    updated_name = "Updated Strategy"
    updated_description = "Updated description"

    user = await create_test_user(dbsession)

    strategies_dao = StrategiesDAO(dbsession)
    await strategies_dao.create_strategy_model(
        name=original_name, description=original_description, user_id=user.id
    )

    # Retrieve the created strategy
    original_strategy = await strategies_dao.get_strategy_model_by_name(original_name)
    assert original_strategy is not None

    # Редактируем стратегию
    updated_strategy = await strategies_dao.update_strategy_model(
        strategy_id=original_strategy.id,
        name=updated_name,
        description=updated_description,
    )

    # Проверяем, что стратегия успешно отредактирована
    assert updated_strategy is not None
    assert updated_strategy.id == original_strategy.id
    assert updated_strategy.name == updated_name
    assert updated_strategy.description == updated_description
