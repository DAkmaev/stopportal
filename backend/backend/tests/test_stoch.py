import uuid
import time

import pytest
from fastapi import FastAPI, Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.db.dao.companies import CompanyDAO


@pytest.mark.anyio
async def test_get_stochs(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """

    :param fastapi_app: current application.
    :param client: client for the app.
    """
    dao = CompanyDAO(dbsession)
    tiker_name = uuid.uuid4().hex
    name = uuid.uuid4().hex
    await dao.create_company_model(tiker_name, name, "MOEX")

    url = fastapi_app.url_path_for("get_stochs")
    response = await client.get(
        url, params={
            'period': 'W',
            'is_cron': 'false',
            'send_messages': 'false',
            'send_test': 'false'
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['decision'] == 'UNKNOWN'

@pytest.mark.anyio
async def test_get_stoch(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """

    :param fastapi_app: current application.
    :param client: client for the app.
    """
    dao = CompanyDAO(dbsession)
    tiker_name = uuid.uuid4().hex
    name = uuid.uuid4().hex
    await dao.create_company_model(tiker_name, name, "MOEX")

    print(f"\nstarted at {time.strftime('%a')}")
    url = fastapi_app.url_path_for("get_stoch", tiker=tiker_name)
    response = await client.get(
        url, params={
            'period': 'W',
            'type': 'MOEX',
            'send_messages': 'false'
        }
    )
    print(f"finished at {time.strftime('%a')}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['decision'] == 'UNKNOWN'

# @pytest.mark.anyio
# async def test_get_stoch_temp(
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     dbsession: AsyncSession,
# ) -> None:
#     """
#
#     :param fastapi_app: current application.
#     :param client: client for the app.
#     """
#     stoch_service = StochService()
#     decision = await stoch_service.get_stochs_test()
#     assert len(decision) == 2
#     assert decision[0].decision == 'RELAX'
#     assert decision[0].tiker == 'A'


