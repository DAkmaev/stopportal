from typing import Any

import pytest

from backend.app.db.dao.ta_decisions import TADecisionDAO
from backend.app.schemas.enums import PeriodEnum
from backend.tests.utils.common import create_test_company, create_test_briefcase
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


@pytest.mark.anyio
@pytest.mark.integrations
async def test_internal_start_generate_ta_decisions(
    celery_local_app,
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()

    # Создаем тестовую компанию в базе данных
    await create_test_company(
        dbsession, need_add_stop=True, need_add_strategy=True, user_id=user.id
    )
    await create_test_briefcase(dbsession, user_id=user.id)

    url = fastapi_app.url_path_for(
        "internal_start_generate_ta_decisions", user_id=user.id
    )
    response = await client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"]


@pytest.mark.anyio
async def test_internal_update_db_decisions(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()

    company = await create_test_company(dbsession, user_id=user.id)
    await create_test_briefcase(dbsession, user_id=user.id)

    url = fastapi_app.url_path_for(
        "internal_update_db_decisions", user_id=user.id
    )
    response = await client.post(
        url,
        json=[
            {
                "tiker": company.tiker,
                "period": "D",
                "last_price": 100.0,
                "k": 10.0,
                "d": 20.0,
                "decision": "SELL"
            }
        ],
    )
    assert response.status_code == status.HTTP_200_OK

    ta_dao = TADecisionDAO(dbsession)
    decisions = await ta_dao.get_ta_decision_models()

    assert len(decisions) == 1
    assert decisions[0].decision == "SELL"
    assert decisions[0].last_price == 100.0
    assert decisions[0].period == PeriodEnum.DAY
    assert decisions[0].company_id == company.id
    assert decisions[0].company.tiker == company.tiker
