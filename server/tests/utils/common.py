import asyncio
import random
import string
import uuid
from typing import Any

from server.src.db.dao.briefcases import BriefcaseDAO
from server.src.db.dao.companies import CompanyDAO
from server.src.db.dao.user import UserDAO
from server.src.db.models.briefcase import (
    BriefcaseModel,
    BriefcaseRegistryModel,
    RegistryOperationEnum,
    BriefcaseShareModel,
)
from server.src.db.models.company import CompanyModel, StopModel, StrategyModel
from server.src.db.models.user import UserModel
from server.src.settings import settings
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

SUPER_USER = "super_admin"


async def create_test_company(
    dbsession: AsyncSession,
    need_add_stop: bool = False,
    need_add_strategy: bool = False,
    tiker_name: str = None,
    name: str = None,
    user_id: int = None,
) -> CompanyModel:
    tiker_name = tiker_name if tiker_name else uuid.uuid4().hex
    name = name if name else uuid.uuid4().hex
    if user_id is None:
        user_id = (await create_test_user(dbsession)).id

    dao = CompanyDAO(dbsession)
    company = await dao.create_company_model(tiker_name, name, "MOEX", user_id)

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
    user_id: int,
) -> list[CompanyModel]:
    dao = CompanyDAO(dbsession)

    tasks = []
    for i in range(count):
        tiker_name: str = uuid.uuid4().hex
        name = uuid.uuid4().hex
        tasks.append(dao.create_company_model(tiker_name, name, "MOEX", user_id))

    await asyncio.gather(*tasks)

    companies = await dao.get_all_companies(user_id=user_id)
    return companies


async def create_test_briefcase(
    dbsession: AsyncSession,
    user_id: int,
    fill_up: float = None,
) -> BriefcaseModel:
    dao = BriefcaseDAO(dbsession)
    await dao.create_briefcase_model(user_id=user_id, fill_up=fill_up)
    briefcases = await dao.get_all_briefcases(user_id=user_id)
    assert briefcases

    return briefcases[-1]


async def create_test_briefcase_registry(
    dbsession: AsyncSession,
    user_id: int,
    briefcase: BriefcaseModel = None,
    company: CompanyModel = None,
    operation: RegistryOperationEnum = RegistryOperationEnum.BUY,
    count: int | None = 10,
    price: float | None = 100.0,
    amount: float = 1000.0,
) -> BriefcaseRegistryModel:
    briefcase_dao = BriefcaseDAO(dbsession)
    company = (
        company if company else await create_test_company(dbsession, user_id=user_id)
    )
    briefcase = (
        briefcase
        if briefcase
        else await create_test_briefcase(dbsession, user_id=user_id)
    )

    # Создаем новую запись briefcase_registry
    await briefcase_dao.create_briefcase_registry_model(
        count=count,
        amount=amount,
        price=price,
        company_id=company.id,
        briefcase_id=briefcase.id,
        operation=operation,
    )

    registry_items = await briefcase_dao.get_all_briefcase_registry(briefcase.id)
    assert registry_items

    return registry_items[-1]


async def create_test_briefcase_share(
    dbsession: AsyncSession,
    user_id: int,
    briefcase: BriefcaseModel = None,
    company: CompanyModel = None,
) -> BriefcaseShareModel:
    briefcase_dao = BriefcaseDAO(dbsession)
    company = (
        company if company else await create_test_company(dbsession, user_id=user_id)
    )
    briefcase = (
        briefcase
        if briefcase
        else await create_test_briefcase(dbsession, user_id=user_id)
    )

    # Создаем новую запись briefcase_share
    await briefcase_dao.create_briefcase_share_model(
        count=100,
        company_id=company.id,
        briefcase_id=briefcase.id,
    )

    shares = await briefcase_dao.get_all_briefcase_shares(briefcase.id)
    assert shares

    return shares[-1]


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
) -> dict[str, Any]:
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
) -> dict[str, Any]:
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
) -> dict[str, Any]:
    user_name = SUPER_USER if is_superuser and not name else random_lower_string()
    email = email if email else random_email()
    user_password = password if password else random_lower_string()
    await create_test_user(
        dbsession,
        is_superuser=is_superuser,
        name=user_name,
        email=email,
        password=user_password,
        is_active=is_active,
    )

    dao = UserDAO(dbsession)
    user = await dao.get_user_by_name(user_name)
    headers = await get_headers(client, fastapi_app, user_name, user_password)

    return {"user": user, "headers": headers}


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
