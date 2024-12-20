import pytest
from backend.app.db.dao.companies import CompanyDAO
from backend.app.db.dao.strategies import StrategiesDAO
from backend.tests.utils.common import create_test_user
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_add_company_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TIKER1"
    NAME = "Company1"
    COMPANY_TYPE = "MOEX"
    company_dao = CompanyDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Ensure the company doesn't already exist
    existing_company = await company_dao.get_company_model_by_tiker(
        tiker=TIKER, user_id=user.id
    )
    assert existing_company is None

    # Create a new company
    await company_dao.create_company_model(
        tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id
    )

    new_company = await company_dao.get_company_model_by_tiker(
        tiker=TIKER, user_id=user.id
    )

    assert new_company is not None
    assert new_company.tiker == TIKER
    assert new_company.name == NAME
    assert new_company.type == COMPANY_TYPE

    # Clean up - delete the test company
    await company_dao.delete_company_model(new_company.id)


@pytest.mark.anyio
async def test_update_company_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"
    NEW_NAME = "Updated Company"
    STRATEGY_NAME1 = "Strategy1"
    STRATEGY_DESCRIPTION1 = "Strategy Description 1"
    STRATEGY_NAME2 = "Strategy2"
    STRATEGY_DESCRIPTION2 = "Strategy Description 2"

    company_dao = CompanyDAO(dbsession)
    strategies_dao = StrategiesDAO(dbsession)

    # Get test user
    user = await create_test_user(dbsession)

    # Create a new company
    await company_dao.create_company_model(
        tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id
    )

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    assert company.name == NAME

    # Add two strategies models for the company
    await strategies_dao.create_strategy_model(
        STRATEGY_NAME1, STRATEGY_DESCRIPTION1, user.id
    )
    await strategies_dao.create_strategy_model(
        STRATEGY_NAME2, STRATEGY_DESCRIPTION2, user.id
    )

    # Retrieve the created company and strategies
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    strategies = await strategies_dao.get_all_strategies_model(user_id=user.id)
    assert company is not None
    assert len(company.strategies) == 0
    assert len(strategies) == 2

    # Update the company
    updated_fields = {
        "name": NEW_NAME,
        "strategies": [{"id": strategies[0].id}, {"id": strategies[1].id}],
    }
    await company_dao.update_company_model(company.id, updated_fields, partial=True)

    # Verify the company was updated
    updated_company = await company_dao.get_company_model_by_tiker(
        tiker=TIKER, user_id=user.id
    )
    assert updated_company is not None
    assert updated_company.name == NEW_NAME
    assert len(updated_company.strategies) == 2

    # Clean up - delete the test company
    await company_dao.delete_company_model(updated_company.id)
    for strategy in strategies:
        await strategies_dao.delete_strategy_model(strategy.id)


@pytest.mark.anyio
async def test_update_company_model_not_found(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    # Test updating a non-existent company
    company_dao = CompanyDAO(dbsession)

    # Try to update a company with an ID that doesn't exist
    non_existent_company_id = 99999
    updated_fields = {"name": "Updated Company"}

    with pytest.raises(HTTPException) as exc_info:
        await company_dao.update_company_model(non_existent_company_id, updated_fields)

    assert exc_info.value.status_code == 404


@pytest.mark.anyio
async def test_delete_company_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"

    company_dao = CompanyDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Create a new company
    await company_dao.create_company_model(
        tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id
    )

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    assert company.name == NAME

    # Delete the company
    await company_dao.delete_company_model(company.id)

    # Verify the company was deleted
    deleted_company = await company_dao.get_company_model_by_tiker(
        tiker=TIKER, user_id=user.id
    )
    assert deleted_company is None


@pytest.mark.anyio
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
async def test_get_all_companies(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    company_dao = CompanyDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Get all companies
    all_companies = await company_dao.get_all_companies(
        limit=10, offset=0, user_id=user.id
    )

    assert len(all_companies) == 0  # Assuming there are no companies at the beginning

    # Create some test companies
    await company_dao.create_company_model(
        tiker="TEST1", name="Company1", company_type="MOEX", user_id=user.id
    )
    await company_dao.create_company_model(
        tiker="TEST2", name="Company2", company_type="MOEX", user_id=user.id
    )

    # Get all companies again
    all_companies = await company_dao.get_all_companies(
        limit=10, offset=0, user_id=user.id
    )

    assert len(all_companies) == 2

    # Clean up - delete the test companies
    for company in all_companies:
        await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_get_company_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"

    company_dao = CompanyDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Create a new company
    await company_dao.create_company_model(
        tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id
    )

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    assert company.name == NAME

    # Clean up - delete the test company
    await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_filter(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    company_dao = CompanyDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Create some test companies
    await company_dao.create_company_model(
        tiker="TEST1", name="Company1", company_type="MOEX", user_id=user.id
    )
    await company_dao.create_company_model(
        tiker="TEST2", name="Company2", company_type="MOEX", user_id=user.id
    )

    # Filter companies by tiker
    filtered_companies = await company_dao.filter(tiker="TEST1")
    assert len(filtered_companies) == 1
    assert filtered_companies[0].tiker == "TEST1"

    # Clean up - delete the test companies
    for company in filtered_companies:
        await company_dao.delete_company_model(company.id)
