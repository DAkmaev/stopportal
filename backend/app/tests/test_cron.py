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
