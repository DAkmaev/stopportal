import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.db.dao.companies import CompanyDAO
from backend.db.models.companies import CompanyModel


async def create_test_company(
    dbsession: AsyncSession,
    need_add_stop: bool = False
) -> CompanyModel:
    dao = CompanyDAO(dbsession)
    tiker_name = uuid.uuid4().hex
    await dao.create_company_model(tiker_name, "MOEX")

    companies = await dao.filter(tiker=tiker_name)

    if need_add_stop:
        await dao.add_stop_model(companies[0].id, "D", 100)
        companies = await dao.filter(tiker=tiker_name)

    return companies[0]

@pytest.mark.anyio
async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests company instance creation."""
    url = fastapi_app.url_path_for("create_company_model")
    tiker_name = uuid.uuid4().hex
    response = await client.post(
        url,
        json={
            "tiker": tiker_name,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    dao = CompanyDAO(dbsession)
    instances = await dao.filter(tiker=tiker_name)
    assert instances[0].tiker == tiker_name


@pytest.mark.anyio
async def test_getting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests company instance retrieval."""
    company = await create_test_company(dbsession)

    url = fastapi_app.url_path_for("get_company_models")
    response = await client.get(url)
    companies = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(companies) == 1
    assert companies[0]["tiker"] == company.tiker


@pytest.mark.anyio
async def test_stop_adding(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests company instance creation."""
    company = await create_test_company(dbsession)

    url = fastapi_app.url_path_for("add_company_stop_model", company_id=company.id)
    response = await client.post(
        url,
        json={
            "period": "D",
            "value": 100
        },
    )
    assert response.status_code == status.HTTP_200_OK

    dao = CompanyDAO(dbsession)
    company_upd = await dao.get_company_model(company.id)
    assert len(company_upd.stops) == 1
    assert company_upd.stops[0].value == 100
    assert company_upd.stops[0].period == 'D'


@pytest.mark.anyio
async def test_stop_deleting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests company stop instance deleting."""
    company = await create_test_company(dbsession, True)
    stop_id = company.stops[0].id

    url = fastapi_app.url_path_for("delete_company_stop_model",
                                   company_id=company.id, stop_id=stop_id)
    response = await client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    dao = CompanyDAO(dbsession)
    stop = await dao.get_company_stop_model(stop_id)
    assert stop is None
