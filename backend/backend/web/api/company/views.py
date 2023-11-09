from typing import List

from fastapi import APIRouter, Depends

from backend.db.dao.companies import CompanyDAO
from backend.db.dao.company_stops import CompanyStopsDAO
from backend.db.models.companies import CompanyModel
from backend.web.api.company.scheme import (
    CompanyModelDTO,
    CompanyModelInputDTO,
    CompanyStopInputDTO, CompanyModelPatchDTO
)

router = APIRouter()


@router.get("/{company_id}", response_model=CompanyModelDTO)
async def get_company_models(
    company_id: int,
    company_dao: CompanyDAO = Depends(),
) -> CompanyModel:
    """
    Retrieve all company objects from the database.

    :param company_dao: DAO for company models.
    :param limit: limit of company objects, defaults to 10.
    :param offset: offset of company objects, defaults to 0.
    :return: list of company objects from database.
    """
    return await company_dao.get_company_model(company_id)

@router.get("/", response_model=List[CompanyModelDTO])
async def get_company_models(
    limit: int = 100,
    offset: int = 0,
    company_dao: CompanyDAO = Depends(),
) -> List[CompanyModel]:
    """
    Retrieve all company objects from the database.

    :param company_dao: DAO for company models.
    :param limit: limit of company objects, defaults to 10.
    :param offset: offset of company objects, defaults to 0.
    :return: list of company objects from database.
    """
    return await company_dao.get_all_companies(limit=limit, offset=offset)


@router.post("/")
async def create_company_model(
    new_company_object: CompanyModelInputDTO,
    company_dao: CompanyDAO = Depends(),
) -> None:
    """
    Creates company model in the database.

    :param new_company_object: new company model item.
    :param company_dao: DAO for company models.
    """
    await company_dao.create_company_model(
        tiker=new_company_object.tiker,
        name=new_company_object.name if new_company_object.name else new_company_object.tiker,
        type=new_company_object.type
    )
    if new_company_object.stops:
        company = await company_dao.get_company_model_by_tiker(new_company_object.tiker)
        for stop in new_company_object.stops:
            await company_dao.add_stop_model(company_id=company.id, period=stop.period,
                                             value=stop.value)


@router.post("/batch")
async def create_company_batch_models(
    new_company_list: List[CompanyModelInputDTO],
    company_dao: CompanyDAO = Depends(),
) -> None:
    """
    Creates companies models in the database.

    :param new_company_list: new companies model items.
    :param company_dao: DAO for company models.
    """

    await company_dao.create_companies_models(
        list(map(lambda s: CompanyModel(
            tiker=s.tiker,
            name=s.name if s.name else s.tiker,
            type=s.type
        ), new_company_list))
    )


@router.patch("/{company_id}")
async def partial_update_company_model(
    company_id: int,
    updated_company: CompanyModelPatchDTO,
    company_dao: CompanyDAO = Depends(),
) -> None:
    """
    Partially updates company model in the database.

    :param updated_company:
    :param company_id: ID of the company to be updated.
    :param updated_fields: Dictionary containing the fields to be updated and their new values.
    :param company_dao: DAO for company models.
    """

    await company_dao.update_company_model(
        company_id, updated_company.model_dump(), True
    )


@router.put("/{company_id}")
async def update_company_model(
    company_id: int,
    updated_company: CompanyModelInputDTO,
    company_dao: CompanyDAO = Depends(),
) -> None:
    """
    Updates company model in the database.

    :param company_id: ID of the company to be updated.
    :param updated_company: Updated company model item.
    :param company_dao: DAO for company models.
    """
    await company_dao.update_company_model(
        company_id, updated_company.model_dump()
    )


@router.post("/{company_id}/stop")
async def add_company_stop_model(
    new_stop: CompanyStopInputDTO,
    company_id: int,
    dao: CompanyStopsDAO = Depends(),
) -> None:
    """
    Creates companies models in the database.

    :param company_id:
    :param new_stop:
    :param company_dao: DAO for company models.
    """

    await dao.add_stop_model(company_id, period=new_stop.period, value=new_stop.value)


@router.delete("/{company_id}", status_code=204)
async def delete_company_model(
    company_id: int,
    company_dao: CompanyDAO = Depends(),
) -> None:
    """
    Delete company model from the database.
    :param company_dao:
    :param company_id:
    """

    await company_dao.delete_company_model(company_id)


@router.delete("/{company_id}/stop/{stop_id}", status_code=204)
async def delete_company_stop_model(
    stop_id: int,
    company_id: int,
    dao: CompanyStopsDAO = Depends(),
) -> None:
    """
    Delete company model from the database.
    :param stop_id:
    :param company_dao:
    """

    await dao.delete_company_stop_model(stop_id, company_id)
