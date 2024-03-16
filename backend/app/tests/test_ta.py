import asyncio
import time
import uuid
from typing import Any
from unittest.mock import patch

import pytest
from pandas import DataFrame

from app.db.dao.companies import CompanyDAO
from app.db.dao.ta_decisions import TADecisionDAO
from app.tests.utils.common import create_test_user, create_test_briefcase
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


@pytest.mark.anyio
async def test_generate_ta_decisions(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    dao = CompanyDAO(dbsession)
    tiker_name1 = uuid.uuid4().hex
    name1 = uuid.uuid4().hex
    tiker_name2 = uuid.uuid4().hex
    name2 = uuid.uuid4().hex
    period = "W"

    user, headers = user_token_headers.values()
    await create_test_briefcase(dbsession, user_id=user.id)

    # create test companies
    await asyncio.gather(
        dao.create_company_model(tiker_name1, name1, "MOEX", user.id),
        dao.create_company_model(tiker_name2, name2, "MOEX", user.id),
    )

    with patch(
        "app.utils.moex.moex_reader.MoexReader.get_company_history"
    ) as mock_method:
        mock_method.return_value = DataFrame()

        url = fastapi_app.url_path_for("generate_ta_decisions")
        response = await client.post(
            url,
            params={
                "period": period,
                "is_cron": "false",
                "send_messages": "false",
                "send_test": "false",
            },
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()[period]["UNKNOWN"])
        assert response.json()["W"]["UNKNOWN"][0]["decision"] == "UNKNOWN"
        assert response.json()["W"]["UNKNOWN"][0]["company"]["tiker"] == tiker_name1


@pytest.mark.anyio
async def test_update_stoch_decisions(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    company_dao = CompanyDAO(dbsession)
    decision_dao = TADecisionDAO(dbsession)
    tiker_name = uuid.uuid4().hex
    name = uuid.uuid4().hex
    period = "W"

    user = await create_test_user(dbsession)
    # Create a test company
    company = await company_dao.create_company_model(tiker_name, name, "MOEX", user.id)

    # Create a StochDecisionModel
    ta_decision = await decision_dao.update_or_create_ta_decision_model(
        None, company, period, "BUY", 0.5, 0.3, 100.0
    )

    # Modify the StochDecisionModel
    updated_decision = "SELL"
    ta_decision = await decision_dao.update_or_create_ta_decision_model(
        ta_decision.id, company, period, updated_decision, 0.4, 0.6, 110.0
    )

    assert ta_decision.decision == updated_decision
    assert ta_decision.k == 0.4
    assert ta_decision.d == 0.6
    assert ta_decision.last_price == 110.0


@pytest.mark.anyio
async def test_generate_ta_decision(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()

    dao = CompanyDAO(dbsession)
    tiker_name = uuid.uuid4().hex
    name = uuid.uuid4().hex
    period = "W"

    await dao.create_company_model(tiker_name, name, "MOEX", user.id)
    with patch(
        "app.utils.moex.moex_reader.MoexReader.get_company_history"
    ) as mock_method:
        mock_method.return_value = DataFrame()

        print(f"\nstarted at {time.strftime('%a')}")
        url = fastapi_app.url_path_for("generate_ta_decision", tiker=tiker_name)
        response = await client.post(
            url,
            params={"period": period, "type": "MOEX", "send_messages": "false"},
            headers=headers,
        )
        print(f"finished at {time.strftime('%a')}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[period]["decision"] == "UNKNOWN"


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
#     user = await create_test_user(dbsession)
#     # create test companies
#     await asyncio.gather(
#         dao.create_company_model(tiker_name1, name1, "MOEX", user.id),
#         # dao.create_company_model(tiker_name2, name2, "MOEX", user.id)
#     )
#
#     url = fastapi_app.url_path_for("generate_ta_decisions")
#     response = await client.post(
#         url, params={
#             'period': period,
#             'is_cron': 'false',
#             'send_messages': 'false',
#             'send_test': 'false'
#         }
#     )
#     assert response.status_code == status.HTTP_200_OK
