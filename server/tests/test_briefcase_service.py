from typing import Any

import pytest
from fastapi import FastAPI, Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from server.src.db.dao.briefcases import BriefcaseDAO
from server.src.db.models.briefcase import RegistryOperationEnum
from server.src.services.briefcase_service import BriefcaseService
from server.tests.utils.common import (
    create_test_briefcase,
    create_test_company,
    create_test_briefcase_registry,
)


@pytest.mark.anyio
async def test_recalculate_share(
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()
    fill_up = 100
    company = await create_test_company(dbsession, user_id=user.id)
    briefcase = await create_test_briefcase(dbsession, user_id=user.id, fill_up=fill_up)

    # покупаем 100
    await create_test_briefcase_registry(
        dbsession,
        user_id=user.id,
        briefcase=briefcase,
        company=company,
        operation=RegistryOperationEnum.BUY,
        count=100,
    )

    # продаем 30
    await create_test_briefcase_registry(
        dbsession,
        user_id=user.id,
        briefcase=briefcase,
        company=company,
        operation=RegistryOperationEnum.SELL,
        count=30,
    )

    # покупаем 10
    await create_test_briefcase_registry(
        dbsession,
        user_id=user.id,
        briefcase=briefcase,
        company=company,
        operation=RegistryOperationEnum.BUY,
        count=10,
    )

    dao: BriefcaseDAO = BriefcaseDAO(dbsession)
    brief_service = BriefcaseService(dbsession)
    await brief_service.recalculate_share(
        company_id=company.id, briefcase_id=briefcase.id
    )

    share = await dao.get_briefcase_share_model_by_company(
        briefcase_id=briefcase.id,
        company_id=company.id,
    )

    assert share
    assert share.count == 80


@pytest.mark.anyio
async def test_recalculate_share_dividends(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()
    fill_up = 100
    company = await create_test_company(dbsession, user_id=user.id)
    briefcase = await create_test_briefcase(dbsession, user_id=user.id, fill_up=fill_up)

    # покупаем 100
    await create_test_briefcase_registry(
        dbsession,
        user_id=user.id,
        briefcase=briefcase,
        company=company,
        operation=RegistryOperationEnum.BUY,
        count=100,
    )

    # получаем дивиденды
    await create_test_briefcase_registry(
        dbsession,
        user_id=user.id,
        briefcase=briefcase,
        company=company,
        operation=RegistryOperationEnum.DIVIDENDS,
        count=None,
        amount=20.0,
    )

    dao: BriefcaseDAO = BriefcaseDAO(dbsession)
    brief_service = BriefcaseService(dbsession)
    await brief_service.recalculate_share(
        company_id=company.id, briefcase_id=briefcase.id
    )

    share = await dao.get_briefcase_share_model_by_company(
        briefcase_id=briefcase.id,
        company_id=company.id,
    )

    assert share
    assert share.count == 100
