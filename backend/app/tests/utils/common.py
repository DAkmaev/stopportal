import asyncio
import random
import string
import uuid

import pytest
from app.db.dao.briefcases import BriefcaseDAO
from app.db.dao.companies import CompanyDAO
from app.db.dao.user import UserDAO
from app.db.models.briefcase import (
    BriefcaseItemModel,
    BriefcaseModel,
    BriefcaseRegistryModel,
    RegistryOperationEnum,
)
from app.db.models.company import CompanyModel, StopModel, StrategyModel
from app.db.models.user import UserModel
from app.settings import settings
from fastapi import Depends, FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def create_test_company(
    dbsession: AsyncSession,
    need_add_stop: bool = False,
    need_add_strategy: bool = False,
    tiker_name: str = None,
    name: str = None,
) -> CompanyModel:
    tiker_name = tiker_name if tiker_name else uuid.uuid4().hex
    name = name if name else uuid.uuid4().hex
    dao = CompanyDAO(dbsession)
    company = await dao.create_company_model(tiker_name, name, "MOEX")

    if need_add_stop:
        company.stops.append(StopModel(company_id=company.id, period="D", value=100))
        company.stops.append(StopModel(company_id=company.id, period="M", value=200))

    if need_add_strategy:
        company.strategies.append(
            StrategyModel(name="TEST1", description="Description1")
        )
        company.strategies.append(
            StrategyModel(name="TEST2", description="Description2")
        )

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
    assert briefcases

    return briefcases[-1]


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


async def create_test_briefcase_registry(
    dbsession: AsyncSession,
    briefcase: BriefcaseModel = None,
    company: CompanyModel = None,
) -> BriefcaseRegistryModel:
    briefcase_dao = BriefcaseDAO(dbsession)
    company = company if company else await create_test_company(dbsession)
    briefcase = briefcase if briefcase else await create_test_briefcase(dbsession)

    # Создаем новую запись briefcase_registry
    await briefcase_dao.create_briefcase_registry_model(
        count=10,
        amount=100.0,
        company_id=company.id,
        briefcase_id=briefcase.id,
        operation=RegistryOperationEnum.BUY,
    )

    registry_items = await briefcase_dao.get_all_briefcase_registry(briefcase.id)
    assert registry_items

    return registry_items[-1]


async def create_test_user(
    dbsession: AsyncSession,
    name: str = None,
    email: str = None,
    password: str = None,
    is_superuser: bool = False,
    is_active: bool = True,
) -> UserModel:
    name = name if name else random_lower_string()
    email = email if email else random_email()
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
    dbsession: AsyncSession,
    name: str = None,
    email: str = None,
    password: str = None,
) -> dict[str, str]:
    return await _get_test_user_headers(
        client,
        fastapi_app,
        dbsession,
        is_superuser=True,
        name=name,
        email=email,
        password=password,
    )


async def get_user_token_headers(
    client: AsyncClient,
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
    name: str = None,
    email: str = None,
    password: str = None,
) -> dict[str, str]:
    return await _get_test_user_headers(
        client,
        fastapi_app,
        dbsession,
        is_superuser=False,
        name=name,
        email=email,
        password=password,
    )


async def get_inactive_user_token_headers(
    client: AsyncClient,
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
    name: str = None,
    email: str = None,
    password: str = None,
) -> dict[str, str]:
    return await _get_test_user_headers(
        client,
        fastapi_app,
        dbsession,
        is_superuser=False,
        is_active=False,
        name=name,
        email=email,
        password=password,
    )


async def _get_test_user_headers(
    client: AsyncClient,
    fastapi_app: FastAPI,
    dbsession: AsyncSession,
    is_superuser: bool,
    name: str = None,
    email: str = None,
    password: str = None,
    is_active: bool = True,
) -> dict[str, str]:
    name = (
        settings.first_superuser if is_superuser and not name else random_lower_string()
    )
    email = email if email else random_email()
    password = (
        settings.first_superuser_password
        if is_superuser and not password
        else random_lower_string()
    )
    await create_test_user(
        dbsession,
        is_superuser=is_superuser,
        name=name,
        email=email,
        password=password,
        is_active=is_active,
    )

    return await get_headers(client, fastapi_app, name, password)


async def get_headers(
    client: AsyncClient, fastapi_app: FastAPI, name: str, password: str
) -> dict[str, str]:
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
