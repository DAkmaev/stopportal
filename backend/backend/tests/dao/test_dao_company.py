import pytest
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.dao.companies import CompanyDAO


@pytest.mark.anyio
async def test_add_company_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TIKER1"
    NAME = "Company1"
    COMPANY_TYPE = "MOEX"
    NEW_NAME = "Company2"
    company_dao = CompanyDAO(dbsession)

    # Ensure the company doesn't already exist
    existing_company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert existing_company is None

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, type="MOEX")

    new_company = await company_dao.get_company_model_by_tiker(tiker=TIKER)

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
    STOP_PERIOD1 = "W"
    STOP_VALUE1 = 100.0
    STOP_PERIOD2 = "M"
    STOP_VALUE2 = 200.0

    company_dao = CompanyDAO(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, type="MOEX")

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert company.name == NAME

    # Add two stop models for the company
    await company_dao.add_stop_model(company.id, STOP_PERIOD1, STOP_VALUE1)
    await company_dao.add_stop_model(company.id, STOP_PERIOD2, STOP_VALUE2)

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert len(company.stops) == 2

    # Update the company
    updated_fields = {
        "name": NEW_NAME,
        "stops": [
            {"period": "M", "value": 300.0, "id": 1},
            {"period": "D", "value": 400.0}
        ]
    }
    await company_dao.update_company_model(company.id, updated_fields, partial=True)

    # Verify the company was updated
    updated_company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert updated_company is not None
    assert updated_company.name == NEW_NAME
    # assert len(updated_company.stops) == 1
    # assert updated_company.stops[0].value == 300

    # Clean up - delete the test company
    await company_dao.delete_company_model(updated_company.id)

@pytest.mark.anyio
async def test_update_company_model_null_values(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"
    NEW_NAME = "Updated Company"
    STOP_PERIOD1 = "W"
    STOP_VALUE1 = 100.0
    STOP_PERIOD2 = "M"
    # STOP_VALUE2 = 200.0

    company_dao = CompanyDAO(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, type="MOEX")

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert company.name == NAME

    # Add stop models for the company
    await company_dao.add_stop_model(company.id, STOP_PERIOD1, STOP_VALUE1)

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert len(company.stops) == 1

    # Update the company
    stop = company.stops[0]
    updated_fields = {
        "stops": [
            {"period": STOP_PERIOD1, "value": None, "id": stop.id},
            {"period": STOP_PERIOD2, "value": None}
        ]
    }
    await company_dao.update_company_model(company.id, updated_fields, partial=True)

    # Verify the company was updated
    updated_company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert updated_company is not None
    assert len(updated_company.stops) == 0

    # Clean up - delete the test company
    await company_dao.delete_company_model(updated_company.id)

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
async def test_add_stop_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"
    STOP_PERIOD = "Weekly"
    STOP_VALUE = 100.0

    company_dao = CompanyDAO(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, type="MOEX")

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert company.name == NAME

    # Add a stop model for the company
    await company_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Verify the stop model was added
    stop_models = company.stops
    assert len(stop_models) == 1
    assert stop_models[0].period == STOP_PERIOD
    assert stop_models[0].value == STOP_VALUE

    # Clean up - delete the test company and its stop
    await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_delete_company_model(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    TIKER = "TEST_TIKER"
    NAME = "Test Company"

    company_dao = CompanyDAO(dbsession)

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, type="MOEX")

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert company.name == NAME

    # Delete the company
    await company_dao.delete_company_model(company.id)

    # Verify the company was deleted
    deleted_company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert deleted_company is None


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

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, type="MOEX")

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert company.name == NAME

    # Add a stop model for the company
    await company_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Retrieve the added stop
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    stop_models = company.stops
    assert len(stop_models) == 1

    # Delete the stop
    await company_dao.delete_company_stop_model(stop_models[0].id, company.id)

    # Verify the stop was deleted
    remaining_stops = await company_dao.get_company_stop_model(stop_models[0].id)
    assert remaining_stops is None

    # Clean up - delete the test company
    await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_get_all_companies(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    company_dao = CompanyDAO(dbsession)

    # Get all companies
    all_companies = await company_dao.get_all_companies(limit=10, offset=0)

    assert len(all_companies) == 0  # Assuming there are no companies at the beginning

    # Create some test companies
    await company_dao.create_company_model(tiker="TEST1", name="Company1", type="MOEX")
    await company_dao.create_company_model(tiker="TEST2", name="Company2", type="MOEX")

    # Get all companies again
    all_companies = await company_dao.get_all_companies(limit=10, offset=0)

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

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, type="MOEX")

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert company.name == NAME

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

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, type="MOEX")

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert company.name == NAME

    # Add a stop model for the company
    await company_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Retrieve the added stop
    company = await company_dao.get_company_model(company.id)
    stop_models = company.stops
    assert len(stop_models) == 1

    # Get the stop using its id
    retrieved_stop = await company_dao.get_company_stop_model(stop_models[0].id)
    assert retrieved_stop is not None
    assert retrieved_stop.period == STOP_PERIOD
    assert retrieved_stop.value == STOP_VALUE

    # Clean up - delete the test company
    await company_dao.delete_company_model(company.id)


@pytest.mark.anyio
async def test_filter(
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
) -> None:
    company_dao = CompanyDAO(dbsession)

    # Create some test companies
    await company_dao.create_company_model(tiker="TEST1", name="Company1", type="MOEX")
    await company_dao.create_company_model(tiker="TEST2", name="Company2", type="MOEX")

    # Filter companies by tiker
    filtered_companies = await company_dao.filter(tiker="TEST1")
    assert len(filtered_companies) == 1
    assert filtered_companies[0].tiker == "TEST1"

    # Clean up - delete the test companies
    for company in filtered_companies:
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

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, type="MOEX")

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert company.name == NAME

    # Add a stop model for the company
    await company_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Retrieve the added stop
    company = await company_dao.get_company_model(company.id)
    stop_models = company.stops
    assert len(stop_models) == 1

    # Update the stop
    stop_model = stop_models[0]
    updated_stop_fields = {"period": "M", "value": 200.0, "id": stop_model.id}
    await company_dao.update_company_stop(company.id, updated_stop_fields)

    # Verify the stop was updated
    stop_model = stop_models[0]
    updated_stop = await company_dao.get_company_stop_model(stop_model.id)
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

    # Create a new company
    await company_dao.create_company_model(tiker=TIKER, name=NAME, type="MOEX")

    # Retrieve the created company
    company = await company_dao.get_company_model_by_tiker(tiker=TIKER)
    assert company.name == NAME

    # Add a stop model for the company
    await company_dao.add_stop_model(company.id, STOP_PERIOD, STOP_VALUE)

    # Retrieve the added stops for the company
    company = await company_dao.get_company_model(company.id)
    stops = company.stops
    assert len(stops) == 1
    assert stops[0].period == STOP_PERIOD
    assert stops[0].value == STOP_VALUE

    # Clean up - delete the test company
    await company_dao.delete_company_model(company.id)
