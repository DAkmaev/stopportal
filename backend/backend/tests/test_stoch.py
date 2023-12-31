import asyncio
import uuid
import time

import pytest
from fastapi import FastAPI, Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.db.dao.briefcases import BriefcaseDAO
from backend.db.dao.companies import CompanyDAO
from backend.db.dao.cron_job import CronJobRunDao
from backend.db.dao.stoch_decisions import StochDecisionDAO
from backend.services.stoch_service import StochService
from backend.tests.utils.common import create_test_company


@pytest.mark.anyio
async def test_generate_stoch_decisions(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """

    :param fastapi_app: current application.
    :param client: client for the app.
    """
    dao = CompanyDAO(dbsession)
    tiker_name1 = uuid.uuid4().hex
    name1 = uuid.uuid4().hex
    tiker_name2 = uuid.uuid4().hex
    name2 = uuid.uuid4().hex
    period = 'W'

    # create test companies
    await asyncio.gather(
        dao.create_company_model(tiker_name1, name1, "MOEX"),
        dao.create_company_model(tiker_name2, name2, "MOEX")
    )

    url = fastapi_app.url_path_for("generate_stoch_decisions")
    response = await client.post(
        url, params={
            'period': period,
            'is_cron': 'false',
            'send_messages': 'false',
            'send_test': 'false'
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()[period]['UNKNOWN'])
    assert response.json()['W']['UNKNOWN'][0]['decision'] == 'UNKNOWN'
    assert response.json()['W']['UNKNOWN'][0]['company']['tiker'] == tiker_name1


@pytest.mark.anyio
async def test_update_stoch_decisions(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    company_dao = CompanyDAO(dbsession)
    decision_dao = StochDecisionDAO(dbsession)
    tiker_name = uuid.uuid4().hex
    name = uuid.uuid4().hex
    period = 'W'

    # Create a test company
    company = await company_dao.create_company_model(tiker_name, name, "MOEX")

    # Create a StochDecisionModel
    stoch_decision = await decision_dao.update_or_create_stoch_decision_model(
        None, company, period, 'BUY', 0.5, 0.3, 100.0
    )

    # Modify the StochDecisionModel
    updated_decision = 'SELL'
    stoch_decision = await decision_dao.update_or_create_stoch_decision_model(
        stoch_decision.id, company, period, updated_decision, 0.4, 0.6, 110.0
    )

    assert stoch_decision.decision == updated_decision
    assert stoch_decision.k == 0.4
    assert stoch_decision.d == 0.6
    assert stoch_decision.last_price == 110.0


@pytest.mark.anyio
async def test_generate_stoch_decision(
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
    period = 'W'
    await dao.create_company_model(tiker_name, name, "MOEX")

    print(f"\nstarted at {time.strftime('%a')}")
    url = fastapi_app.url_path_for("generate_stoch_decision", tiker=tiker_name)
    response = await client.post(
        url, params={
            'period': period,
            'type': 'MOEX',
            'send_messages': 'false'
        }
    )
    print(f"finished at {time.strftime('%a')}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[period]['decision'] == 'UNKNOWN'




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
#     dao = CompanyDAO(dbsession)
#     tiker_name1 = 'LKOH'
#     name1 = 'Лукойл'
#     # tiker_name2 = uuid.uuid4().hex
#     # name2 = uuid.uuid4().hex
#     period = 'ALL'
#
#     # create test companies
#     await asyncio.gather(
#         dao.create_company_model(tiker_name1, name1, "MOEX"),
#         # dao.create_company_model(tiker_name2, name2, "MOEX")
#     )
#
#     url = fastapi_app.url_path_for("generate_stoch_decisions")
#     response = await client.post(
#         url, params={
#             'period': period,
#             'is_cron': 'false',
#             'send_messages': 'false',
#             'send_test': 'false'
#         }
#     )
#     assert response.status_code == status.HTTP_200_OK



