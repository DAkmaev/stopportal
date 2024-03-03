from typing import Any

import pytest

from app.db.dao.briefcases import BriefcaseDAO
from app.db.dao.companies import CompanyDAO
from app.db.dao.stops import StopsDAO
from app.tests.utils.common import create_test_company, create_test_briefcase
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


@pytest.mark.anyio
async def test_cron_ta(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()
    await create_test_briefcase(dbsession, user_id=user.id)

    url = fastapi_app.url_path_for("cron_generate_ta_decisions", user_id=user.id)
    response = await client.post(
        url,
        json={},
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_stop_deleting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Tests company stop instance deleting."""
    user, headers = user_token_headers.values()
    company = await create_test_company(dbsession, need_add_stop=True, user_id=user.id)
    stop_id = company.stops[0].id

    url = fastapi_app.url_path_for("delete_stop_model", stop_id=stop_id)
    response = await client.delete(url, headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    dao = StopsDAO(dbsession)
    stop = await dao.get_stop_model(stop_id)
    assert stop is None


@pytest.mark.anyio
async def test_stop_updating(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    """Tests updating a stop model."""
    user, headers = user_token_headers.values()
    company = await create_test_company(dbsession, need_add_stop=True, user_id=user.id)
    stop = company.stops[0]

    # Сформируем данные для обновления стопа
    updated_period = "W"
    updated_value = 150
    updated_stop_data = {
        "id": stop.id,
        "company_id": company.id,
        "period": updated_period,
        "value": updated_value,
    }

    # Отправляем PUT-запрос для обновления стопа
    url = fastapi_app.url_path_for("update_stop_model")
    response = await client.put(url, json=updated_stop_data, headers=headers)

    # Проверяем успешный ответ
    assert response.status_code == status.HTTP_200_OK

    # Проверяем обновление стопа в базе данных
    dao = StopsDAO(dbsession)
    updated_stop = await dao.get_stop_model(stop.id)
    assert updated_stop is not None
    assert updated_stop.period == updated_period
    assert updated_stop.value == updated_value
