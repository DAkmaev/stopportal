from server.src.db.dao.companies import CompanyDAO
from server.src.db.dao.stops import StopsDAO
from server.src.api.stop.scheme import StopDTO, StopInputDTO
from server.src.auth import CurrentUser, check_owner_or_superuser
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/")
async def add_stop(
    new_stop: StopInputDTO,
    current_user: CurrentUser,
    company_dao: CompanyDAO = Depends(),
    dao: StopsDAO = Depends(),
) -> None:
    exist_company = await company_dao.get_company_model(new_stop.company_id)
    await check_owner_or_superuser(exist_company.user_id, current_user)

    await dao.add_stop_model(
        company_id=new_stop.company_id,
        period=new_stop.period,
        value=new_stop.value,
    )


@router.delete("/{stop_id}", status_code=204)
async def delete_stop(
    stop_id: int,
    current_user: CurrentUser,
    dao: StopsDAO = Depends(),
    company_dao: CompanyDAO = Depends(),
) -> None:
    exist_stop = await dao.get_stop_model(stop_id=stop_id)
    exist_company = await company_dao.get_company_model(exist_stop.company_id)
    await check_owner_or_superuser(exist_company.user_id, current_user)

    await dao.delete_stop_model(stop_id)


@router.put("/")
async def update_stop(
    updated_stop: StopDTO,
    current_user: CurrentUser,
    dao: StopsDAO = Depends(),
    company_dao: CompanyDAO = Depends(),
) -> None:
    exist_company = await company_dao.get_company_model(updated_stop.company_id)
    await check_owner_or_superuser(exist_company.user_id, current_user)

    await dao.update_stop_model(updated_stop.model_dump())
