import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.db.dao.companies import CompanyDAO
from backend.db.dao.stops import StopsDAO
from backend.tests.utils.common import create_test_company


@pytest.mark.anyio
async def test_stop_adding(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests company instance creation."""
    company = await create_test_company(dbsession)

    url = fastapi_app.url_path_for("add_company_stop_model")
    response = await client.post(
        url,
        json={
            "company_id": company.id,
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

    url = fastapi_app.url_path_for("delete_company_stop_model", stop_id=stop_id)
    response = await client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    dao = StopsDAO(dbsession)
    stop = await dao.get_company_stop_model(stop_id)
    assert stop is None
