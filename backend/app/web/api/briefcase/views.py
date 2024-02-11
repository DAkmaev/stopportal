from datetime import datetime
from typing import List

from app.db.dao.briefcases import BriefcaseDAO
from app.db.models.briefcase import (
    BriefcaseItemModel,
    BriefcaseModel,
    BriefcaseRegistryModel,
)
from app.web.api.briefcase.scheme import (
    BriefcaseDTO,
    BriefcaseInputDTO,
    BriefcaseItemDTO,
    BriefcaseItemInputDTO,
    BriefcaseRegistryDTO,
    BriefcaseRegistryInputDTO,
)
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/{briefcase_id}", response_model=BriefcaseDTO)
async def get_briefcase_model(
    briefcase_id: int,
    dao: BriefcaseDAO = Depends(),
) -> BriefcaseModel:
    return await dao.get_briefcase_model(briefcase_id)


@router.get("/", response_model=List[BriefcaseDTO])
async def get_briefcase_models(
    limit: int = 100,
    offset: int = 0,
    dao: BriefcaseDAO = Depends(),
) -> List[BriefcaseModel]:
    return await dao.get_all_briefcases(limit=limit, offset=offset)


@router.post("/")
async def create_briefcase_model(
    new_briefcase_object: BriefcaseInputDTO,
    dao: BriefcaseDAO = Depends(),
) -> None:
    await dao.create_briefcase_model(fill_up=new_briefcase_object.fill_up)


@router.put("/{briefcase_id}")
async def update_briefcase_model(
    briefcase_id: int,
    updated_briefcase: BriefcaseInputDTO,
    briefcase_dao: BriefcaseDAO = Depends(),
) -> None:
    await briefcase_dao.update_briefcase_model(briefcase_id, updated_briefcase.fill_up)


@router.delete("/{briefcase_id}", status_code=204)
async def delete_briefcase_model(
    briefcase_id: int,
    briefcase_dao: BriefcaseDAO = Depends(),
) -> None:
    await briefcase_dao.delete_briefcase_model(briefcase_id)


@router.get("/items/{item_id}", response_model=BriefcaseItemDTO)
async def get_briefcase_item(
    item_id: int,
    dao: BriefcaseDAO = Depends(),
) -> BriefcaseItemModel:
    return await dao.get_briefcase_item_model(item_id)


@router.get("/{briefcase_id}/items/", response_model=List[BriefcaseItemDTO])
async def get_briefcase_items(
    briefcase_id: int,
    dao: BriefcaseDAO = Depends(),
) -> List[BriefcaseItemModel]:
    return await dao.get_all_briefcase_items()


@router.post("/{briefcase_id}/items/")
async def create_briefcase_item_model(
    briefcase_id: int,
    new_item: BriefcaseItemInputDTO,  # Assuming you have a DTO for creating items
    dao: BriefcaseDAO = Depends(),
) -> None:
    await dao.create_briefcase_item_model(
        count=new_item.count,
        dividends=new_item.dividends,
        company_id=new_item.company.id,
        strategy_id=new_item.strategy.id if new_item.strategy else None,
        briefcase_id=briefcase_id,
    )


@router.put("/items/{item_id}")
async def update_briefcase_item(
    item_id: int,
    updated_item: BriefcaseItemInputDTO,  # Assuming DTO for updating items
    dao: BriefcaseDAO = Depends(),
) -> None:
    # Similar to creation, you'll need to pass the updated attributes to
    # update_briefcase_item_model
    await dao.update_briefcase_item_model(
        briefcase_item_id=item_id,
        count=updated_item.count,
        dividends=updated_item.dividends,
    )


@router.delete("/items/{item_id}", status_code=204)
async def delete_briefcase_item(
    item_id: int,
    dao: BriefcaseDAO = Depends(),
) -> None:
    """
    Delete a specific item from a briefcase.

    :param item_id: ID of the BriefcaseItemModel to delete.
    :param dao: DAO for Briefcase models.
    """
    await dao.delete_briefcase_item_model(item_id)


@router.get("/registry/{item_id}", response_model=BriefcaseRegistryDTO)
async def get_briefcase_registry(
    item_id: int,
    dao: BriefcaseDAO = Depends(),
) -> BriefcaseRegistryModel:
    return await dao.get_briefcase_registry_model(item_id)


@router.get("/{briefcase_id}/registry/", response_model=List[BriefcaseRegistryDTO])
async def get_briefcase_registries(  # noqa: WPS211
    briefcase_id: int,
    dao: BriefcaseDAO = Depends(),
    limit: int = 100000,
    offset: int = 0,
    date_from: str = None,
    date_to: str = None,
) -> List[BriefcaseRegistryModel]:
    return await dao.get_all_briefcase_registry(
        briefcase_id=briefcase_id,
        limit=limit,
        offset=offset,
        date_from=datetime.strptime(date_from, "%Y-%m-%d") if date_from else None,
        date_to=datetime.strptime(date_to, "%Y-%m-%d") if date_to else None,
    )


@router.post("/{briefcase_id}/registry/")
async def create_briefcase_registry_model(
    briefcase_id: int,
    new_item: BriefcaseRegistryInputDTO,  # Assuming you have a DTO for creating items
    dao: BriefcaseDAO = Depends(),
) -> None:
    await dao.create_briefcase_registry_model(
        count=new_item.count,
        amount=new_item.amount,
        company_id=new_item.company.id,
        briefcase_id=briefcase_id,
        operation=new_item.operation,
        strategy_id=new_item.strategy.id if new_item.strategy else None,
        created_date=new_item.created_date if new_item.created_date else None,
        price=new_item.price,
        currency=new_item.currency,
    )


@router.put("/registry/{item_id}")
async def update_briefcase_registry(
    item_id: int,
    updated_item: BriefcaseRegistryInputDTO,
    dao: BriefcaseDAO = Depends(),
) -> None:
    await dao.update_briefcase_registry_model(
        registry_id=item_id,
        updated_fields=updated_item.model_dump(),
    )


@router.delete("/registry/{item_id}", status_code=204)
async def delete_briefcase_registry(
    item_id: int,
    dao: BriefcaseDAO = Depends(),
) -> None:
    await dao.delete_briefcase_registry_model(item_id)
