import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dao.briefcases import BriefcaseDAO
from backend.db.dao.companies import CompanyDAO
from backend.db.dao.stops import StopsDAO
from backend.db.models.briefcase import BriefcaseItemModel, BriefcaseModel
from backend.db.models.company import CompanyModel, StopModel, StrategyModel


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