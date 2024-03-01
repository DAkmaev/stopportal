import pytest
from app.db.dao.companies import CompanyDAO
from app.db.dao.stops import StopsDAO
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.utils.common import create_test_user


@pytest.mark.anyio
async def test_add_stop_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"
    STOP_PERIOD = "Weekly"
    STOP_VALUE = 100.0

    company_dao = CompanyDAO(dbsession)
    company_stops_dao = StopsDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id)

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    assert company.name == NAME

    # Add a stop model for the company
    await company_stops_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Verify the stop model was added
    stop_models = company.stops
    assert len(stop_models) == 1
    assert stop_models[0].period == STOP_PERIOD
    assert stop_models[0].value == STOP_VALUE

    # Clean up - delete the test company and its stop
    await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_delete_company_stop_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"
    STOP_PERIOD = "Weekly"
    STOP_VALUE = 100.0

    company_dao = CompanyDAO(dbsession)
    company_stops_dao = StopsDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id)

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    assert company.name == NAME

    # Add a stop model for the company
    await company_stops_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Retrieve the added stop
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    stop_models = company.stops
    assert len(stop_models) == 1

    # Delete the stop
    await company_stops_dao.delete_stop_model(stop_models[0].id)

    # Verify the stop was deleted
    remaining_stops = await company_stops_dao.get_stop_model(stop_models[0].id)
    assert remaining_stops is None

    # Clean up - delete the test company
    await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_get_company_stop_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"
    STOP_PERIOD = "Weekly"
    STOP_VALUE = 100.0

    company_dao = CompanyDAO(dbsession)
    company_stops_dao = StopsDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id)

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    assert company.name == NAME

    # Add a stop model for the company
    await company_stops_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Retrieve the added stop
    company = await company_dao.get_company_model(company.id)
    stop_models = company.stops
    assert len(stop_models) == 1

    # Get the stop using its id
    retrieved_stop = await company_stops_dao.get_stop_model(stop_models[0].id)
    assert retrieved_stop is not None
    assert retrieved_stop.period == STOP_PERIOD
    assert retrieved_stop.value == STOP_VALUE

    # Clean up - delete the test company
    await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_update_company_stop_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"
    STOP_PERIOD = "W"
    STOP_VALUE = 100.0

    company_dao = CompanyDAO(dbsession)
    company_stops_dao = StopsDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id)

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    assert company.name == NAME

    # Add a stop model for the company
    await company_stops_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Retrieve the added stop
    company = await company_dao.get_company_model(company.id)
    stop_models = company.stops
    assert len(stop_models) == 1

    # Update the stop
    stop_model = stop_models[0]
    updated_stop_fields = {"period": "M", "value": 200.0, "id": stop_model.id}
    await company_stops_dao.update_stop_model(updated_stop_fields)

    # Verify the stop was updated
    stop_model = stop_models[0]
    updated_stop = await company_stops_dao.get_stop_model(stop_model.id)
    assert updated_stop is not None
    assert updated_stop.period == "M"
    assert updated_stop.value == 200.0

    # Clean up - delete the test company
    await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_get_company_stops_by_id(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"
    STOP_PERIOD = "W"
    STOP_VALUE = 100.0

    company_dao = CompanyDAO(dbsession)
    company_stops_dao = StopsDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id)

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    assert company.name == NAME

    # Add a stop model for the company
    await company_stops_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Retrieve the added stops for the company
    company = await company_dao.get_company_model(company.id)
    stops = company.stops
    assert len(stops) == 1
    assert stops[0].period == STOP_PERIOD
    assert stops[0].value == STOP_VALUE

    # Clean up - delete the test company
    await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_add_stop_model_prevent_duplicate(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"
    STOP_PERIOD = "W"
    STOP_VALUE = 100.0

    company_dao = CompanyDAO(dbsession)
    company_stops_dao = StopsDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id)

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    assert company.name == NAME

    # Add a stop model for the company with a specific period
    await company_stops_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)

    # Attempt to add a stop model with the same period for the same company
    with pytest.raises(HTTPException) as exc_info:
        await company_stops_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Verify that the attempt to add a duplicate stop was prevented
    assert exc_info.value.status_code == 400

    # Clean up - delete the test company
    await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_update_stop_model_prevent_duplicate(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"
    STOP_PERIOD1 = "W"
    STOP_PERIOD2 = "D"
    STOP_VALUE = 100.0

    company_dao = CompanyDAO(dbsession)
    company_stops_dao = StopsDAO(dbsession)

    # Create test user
    user = await create_test_user(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, company_type="MOEX", user_id=user.id)

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER, user_id=user.id)
    assert company.name == NAME

    # Add a stop model for the company
    await company_stops_dao.add_stop_model(company.id, STOP_PERIOD1, STOP_VALUE)
    await company_stops_dao.add_stop_model(company.id, STOP_PERIOD2, STOP_VALUE)

    # Retrieve the added stop
    company = await company_dao.get_company_model(company.id)
    stop_models = company.stops
    assert len(stop_models) == 2

    # Attempt to update the stop model to a period that already exists for the
    # same company
    updated_stop_fields = {
        "company_id": company.id,
        "value": 200.0,
        "id": stop_models[0].id,
        "period": stop_models[1].period,
    }
    with pytest.raises(HTTPException) as exc_info:
        await company_stops_dao.update_stop_model(updated_stop_fields)

    # Verify that the attempt to update the stop to a duplicate period was prevented
    assert exc_info.value.status_code == 400

    # Clean up - delete the test company
    await company_dao.delete_company_model(company.id)
