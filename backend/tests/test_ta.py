from typing import Any

import pytest

from backend.app.db.dao.ta_decisions import TADecisionDAO
from backend.tests.utils.common import create_test_company, create_test_briefcase
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


@pytest.mark.anyio
@pytest.mark.integrations
async def test_run_generate_ts_decisions(
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

    url = fastapi_app.url_path_for("run_generate_ts_decisions")
    response = await client.post(
        url,
        json={},
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"]


@pytest.mark.anyio
@pytest.mark.integrations
async def test_run_generate_ts_decisions_no_briefcase(
    celery_local_app,
    fastapi_app: FastAPI,
    client: AsyncClient,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()
    url = fastapi_app.url_path_for("run_generate_ts_decisions")
    response = await client.post(
        url,
        json={},
        headers=headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
@pytest.mark.integrations
async def test_get_task_status(
    celery_local_app,
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()

    await create_test_briefcase(dbsession, user_id=user.id)
    url = fastapi_app.url_path_for("run_generate_ts_decisions")
    response = await client.post(
        url,
        json={},
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK

    task_id = response.json()["id"]
    url_check = fastapi_app.url_path_for("get_task_status", task_id=task_id)
    response_check = await client.get(url_check)

    assert response_check.status_code == status.HTTP_200_OK
    task_status = response_check.json()["status"]
    assert task_status in ["PENDING", "SUCCESS"]


@pytest.mark.anyio
async def test_get_ts_decisions(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()
    # Create a test companies
    company = await create_test_company(dbsession, user_id=user.id)

    # Create a DecisionModel
    decision_dao = TADecisionDAO(dbsession)
    await decision_dao.update_or_create_ta_decision_model(
        company, "D", "BUY", 0.1, 0.2, 1.0
    )

    url = fastapi_app.url_path_for("get_ts_decisions")
    response = await client.get(
        url,
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()[0]
    assert body["tiker"] == company.tiker
    assert body["decision"] == "BUY"
    assert body["k"] == 0.1
    assert body["d"] == 0.2
    assert body["period"] == "D"
    assert body["last_price"] is None
