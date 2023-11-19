import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dao.companies import CompanyDAO
from backend.db.dao.stops import StopsDAO
from backend.db.models.companies import CompanyModel, StopModel, StrategyModel


async def create_test_company(
    dbsession: AsyncSession,
    need_add_stop: bool = False,
    need_add_strategy: bool = False
) -> CompanyModel:
    dao = CompanyDAO(dbsession)
    stops_dao = StopsDAO(dbsession)
    tiker_name = uuid.uuid4().hex
    name = uuid.uuid4().hex
    company = await dao.create_company_model(tiker_name, name, "MOEX")

    if need_add_stop:
        company.stops.append(StopModel(company_id=company.id, period='D', value=100))
        company.stops.append(StopModel(company_id=company.id, period='M', value=200))

    if need_add_strategy:
        company.strategies.append(StrategyModel(name="TEST1", description="Description1"))
        company.strategies.append(StrategyModel(name="TEST2", description="Description2"))

    companies = await dao.filter(tiker=tiker_name)
    return companies[0]
