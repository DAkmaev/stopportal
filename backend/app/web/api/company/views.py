from typing import List

from app.db.dao.companies import CompanyDAO
from app.db.models.company import CompanyModel
from app.web.api.company.scheme import (
    CompanyModelDTO,
    CompanyModelInputDTO,
    CompanyModelPatchDTO,
)
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/{company_id}", response_model=CompanyModelDTO)
async def get_company_model(
    company_id: int,
    company_dao: CompanyDAO = Depends(),
) -> CompanyModel:
    return await company_dao.get_company_model(company_id)


@router.get("/", response_model=List[CompanyModelDTO])
async def get_company_models(
    limit: int = 100,
    offset: int = 0,
    company_dao: CompanyDAO = Depends(),
) -> List[CompanyModel]:
    return await company_dao.get_all_companies(limit=limit, offset=offset)


@router.post("/")
async def create_company_model(
    new_company_object: CompanyModelInputDTO,
    company_dao: CompanyDAO = Depends(),
) -> None:
    await company_dao.create_company_model(
        tiker=new_company_object.tiker,
        name=new_company_object.name if new_company_object.name else new_company_object.tiker,
        company_type=new_company_object.type,
        strategies=[
            strategy.id for strategy in new_company_object.strategies
        ] if new_company_object.strategies else None,
    )


@router.post("/batch")
async def create_company_batch_models(
    new_company_list: List[CompanyModelInputDTO],
    company_dao: CompanyDAO = Depends(),
) -> None:
    await company_dao.create_companies_models([
        CompanyModel(
            tiker=comp.tiker,
            name=comp.name if comp.name else comp.tiker,
            type=comp.type,
        ) for comp in new_company_list
    ])


@router.patch("/{company_id}")
async def partial_update_company_model(
    company_id: int,
    updated_company: CompanyModelPatchDTO,
    company_dao: CompanyDAO = Depends(),
) -> None:
    await company_dao.update_company_model(
        company_id, updated_company.model_dump(), True,  # noqa: WPS425
    )


@router.put("/{company_id}")
async def update_company_model(
    company_id: int,
    updated_company: CompanyModelInputDTO,
    company_dao: CompanyDAO = Depends(),
) -> None:
    await company_dao.update_company_model(company_id, updated_company.model_dump())


@router.delete("/{company_id}", status_code=204)
async def delete_company_model(
    company_id: int,
    company_dao: CompanyDAO = Depends(),
) -> None:
    await company_dao.delete_company_model(company_id)
