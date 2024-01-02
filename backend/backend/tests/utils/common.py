import asyncio
import random
import string
import uuid

import pytest
from fastapi import FastAPI, Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dao.briefcases import BriefcaseDAO
from backend.db.dao.companies import CompanyDAO
from backend.db.dao.user import UserDAO
from backend.db.models.briefcase import BriefcaseItemModel, BriefcaseModel
from backend.db.models.company import CompanyModel, StopModel, StrategyModel
from backend.db.models.user import UserModel
from backend.settings import settings


async def create_test_company(
    dbsession: AsyncSession,
    need_add_stop: bool = False,
    need_add_strategy: bool = False,
    tiker_name: str = uuid.uuid4().hex,
    name = uuid.uuid4().hex
) -> CompanyModel:
    dao = CompanyDAO(dbsession)
    company = await dao.create_company_model(tiker_name, name, "MOEX")

    if need_add_stop:
        company.stops.append(StopModel(company_id=company.id, period='D', value=100))
        company.stops.append(StopModel(company_id=company.id, period='M', value=200))

    if need_add_strategy:
        company.strategies.append(StrategyModel(name="TEST1", description="Description1"))
        company.strategies.append(StrategyModel(name="TEST2", description="Description2"))

    companies = await dao.filter(tiker=tiker_name)
    return companies[0]


async def create_test_companies(
    dbsession: AsyncSession,
    count: int,
) -> list[CompanyModel]:
    dao = CompanyDAO(dbsession)

    tasks = []
    for i in range(count):
        tiker_name: str = uuid.uuid4().hex
        name = uuid.uuid4().hex
        tasks.append(dao.create_company_model(tiker_name, name, "MOEX"))

    await asyncio.gather(*tasks)

    companies = await dao.get_all_companies()
    return companies


async def create_test_briefcase(
    dbsession: AsyncSession,
) -> BriefcaseModel:
    dao = BriefcaseDAO(dbsession)
    await dao.create_briefcase_model()
    briefcases = await dao.get_all_briefcases()
    assert len(briefcases) == 1

    return briefcases[0]


async def create_test_briefcase_item(
    dbsession: AsyncSession,
) -> BriefcaseItemModel:
    company = await create_test_company(dbsession)
    briefcase = await create_test_briefcase(dbsession)
    dao = BriefcaseDAO(dbsession)
    await dao.create_briefcase_item_model(
        count=1, dividends=10, company_id=company.id, briefcase_id=briefcase.id
    )
    briefcase_items = await dao.get_all_briefcase_items()
    assert len(briefcase_items) == 1

    return briefcase_items[0]


async def create_test_user(
    dbsession: AsyncSession,
    name: str = None,
    email: str = None,
    password: str = None,
    is_superuser: bool = False,
    is_active: bool = True,
) -> UserModel:
    name = name if name else random_lower_string()
    email = name if email else random_email()
    password = password if password else random_lower_string()

    dao = UserDAO(dbsession)

    await dao.create_user_model(name, email, password, is_superuser, is_active)
    user = await dao.get_user_by_name(name)

    assert user

    return user


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


async def get_superuser_token_headers(
    client: AsyncClient,
    fastapi_app: FastAPI,
    dbsession: AsyncSession
) -> dict[str, str]:
    return await _get_headers(client, fastapi_app, dbsession, is_superuser=True)


async def get_user_token_headers(
    client: AsyncClient,
    fastapi_app: FastAPI,
    dbsession: AsyncSession
) -> dict[str, str]:
    return await _get_headers(client, fastapi_app, dbsession, is_superuser=False)


async def _get_headers(
    client: AsyncClient,
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
    is_superuser: bool,
    # name: str = random_lower_string(),
    # email: str = random_email(),
    # password: str = random_lower_string()
) -> dict[str, str]:
    name = settings.FIRST_SUPERUSER if is_superuser else random_lower_string()
    password = settings.FIRST_SUPERUSER_PASSWORD if is_superuser else random_lower_string()
    email = random_email()
    await create_test_user(
        dbsession, is_superuser=is_superuser,
        name=name,
        email=email,
        password=password,
    )
    login_data = {
        "username": name,
        "password": password,
    }
    url = fastapi_app.url_path_for("login_access_token")
    response = await client.post(url, data=login_data)
    tokens = response.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
