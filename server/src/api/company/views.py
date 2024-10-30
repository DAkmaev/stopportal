import logging
from typing import List

from server.src.db.dao.companies import CompanyDAO
from server.src.db.models.company import CompanyModel
from server.src.api.company.scheme import (
    CompanyModelDTO,
    CompanyModelInputDTO,
    CompanyModelPatchDTO,
)
from server.src.auth import CurrentUser, check_owner_or_superuser
from fastapi import APIRouter, Depends

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{company_id}", response_model=CompanyModelDTO)
async def get_company(
    company_id: int,
    current_user: CurrentUser,
    company_dao: CompanyDAO = Depends(),
) -> CompanyModel:
    exist_company = await company_dao.get_company_model(company_id)
    await check_owner_or_superuser(exist_company.user_id, current_user)
    return exist_company


@router.get("/", response_model=List[CompanyModelDTO])
async def get_company(
    current_user: CurrentUser,
    limit: int = 100,
    offset: int = 0,
    company_dao: CompanyDAO = Depends(),
) -> List[CompanyModel]:
    return await company_dao.get_all_companies(
        limit=limit,
        offset=offset,
        user_id=current_user.id,
    )


@router.post("/")
async def create_company(
    new_company_object: CompanyModelInputDTO,
    current_user: CurrentUser,
    company_dao: CompanyDAO = Depends(),
) -> None:
    company = await company_dao.create_company_model(
        tiker=new_company_object.tiker,
        name=new_company_object.name,
        company_type=new_company_object.type,
        strategies=new_company_object.strategies,
        user_id=current_user.id,
    )
    logger.info(f"Created company model for name={company.name}")


@router.post("/batch")
async def create_company_batch(
    new_company_list: List[CompanyModelInputDTO],
    current_user: CurrentUser,
    company_dao: CompanyDAO = Depends(),
) -> None:
    await company_dao.create_companies_models(
        [
            CompanyModel(
                tiker=comp.tiker,
                name=comp.name if comp.name else comp.tiker,
                type=comp.type,
                user=current_user,
            )
            for comp in new_company_list
        ],
    )


@router.patch("/{company_id}")
async def partial_update_company(
    company_id: int,
    updated_company: CompanyModelPatchDTO,
    current_user: CurrentUser,
    company_dao: CompanyDAO = Depends(),
) -> None:
    exist_company = await company_dao.get_company_model(company_id)
    await check_owner_or_superuser(exist_company.user_id, current_user)

    await company_dao.update_company_model(
        company_id,
        updated_company.model_dump(),
        True,  # noqa: WPS425
    )


@router.put("/{company_id}")
async def update_company(
    company_id: int,
    updated_company: CompanyModelInputDTO,
    current_user: CurrentUser,
    company_dao: CompanyDAO = Depends(),
) -> None:
    exist_company = await company_dao.get_company_model(company_id)
    await check_owner_or_superuser(exist_company.user_id, current_user)

    await company_dao.update_company_model(
        company_id,
        updated_company.model_dump(),
    )


@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: int,
    current_user: CurrentUser,
    company_dao: CompanyDAO = Depends(),
) -> None:
    exist_company = await company_dao.get_company_model(company_id)
    await check_owner_or_superuser(exist_company.user_id, current_user)

    await company_dao.delete_company_model(company_id)
