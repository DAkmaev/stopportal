from typing import Any

import pytest
from server.tests.utils.common import create_test_company
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


@pytest.mark.anyio
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

    url = fastapi_app.url_path_for("internal_start_generate_ta_decisions", user_id=user.id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id']
