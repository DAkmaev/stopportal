from typing import List

from fastapi import APIRouter, Depends

from backend.db.dao.briefcases import BriefcaseDAO
from backend.db.models.briefcase import BriefcaseModel, BriefcaseItemModel
from backend.web.api.briefcase.scheme import (BriefcaseDTO, BriefcaseInputDTO,
                                              BriefcaseItemInputDTO, BriefcaseItemDTO)

router = APIRouter()


@router.get("/{briefcase_id}", response_model=BriefcaseDTO)
async def get_briefcase_models(
    briefcase_id: int,
    dao: BriefcaseDAO = Depends(),
) -> BriefcaseModel:
    """
    Retrieve BriefcaseModel object by id from the database.

    :param dao:
    :param briefcase_id: DAO for Briefcase models.
    """
    return await dao.get_briefcase_model(briefcase_id)


@router.get("/", response_model=List[BriefcaseDTO])
async def get_briefcase_models(
    limit: int = 100,
    offset: int = 0,
    dao: BriefcaseDAO = Depends(),
) -> List[BriefcaseModel]:
    """
    Retrieve all briefcase objects from the database.

    :param dao:
    :param limit: limit of briefcase objects, defaults to 100.
    :param offset: offset of briefcase objects, defaults to 0.
    :return: list of briefcase from database.
    """
    return await dao.get_all_briefcases(limit=limit, offset=offset)


@router.post("/")
async def create_briefcase_model(
    new_briefcase_object: BriefcaseInputDTO,
    dao: BriefcaseDAO = Depends(),
) -> None:
    """
    Creates briefcase model in the database.

    :param new_briefcase_object: new briefcase model item.
    :param dao: DAO for briefcase models.
    """
    await dao.create_briefcase_model(
        fill_up=new_briefcase_object.fill_up
    )


@router.put("/{briefcase_id}")
async def update_briefcase_model(
    briefcase_id: int,
    updated_briefcase: BriefcaseInputDTO,
    briefcase_dao: BriefcaseDAO = Depends(),
) -> None:
    """
    Updates briefcase model in the database.

    :param briefcase_id: ID of the briefcase to be updated.
    :param updated_briefcase: Updated briefcase model item.
    :param briefcase_dao: DAO for briefcase models.
    """
    await briefcase_dao.update_briefcase_model(
        briefcase_id, updated_briefcase.fill_up
    )


@router.delete("/{briefcase_id}", status_code=204)
async def delete_briefcase_model(
    briefcase_id: int,
    briefcase_dao: BriefcaseDAO = Depends(),
) -> None:
    """
    Delete briefcase model from the database.
    :param briefcase_dao:
    :param briefcase_id:
    """

    await briefcase_dao.delete_briefcase_model(briefcase_id)


@router.get("/items/{item_id}", response_model=BriefcaseItemDTO)
async def get_briefcase_item(
    item_id: int,
    dao: BriefcaseDAO = Depends(),
) -> BriefcaseItemModel:
    """
    Retrieve BriefcaseItemModel object by id from the database.

    :param item_id: ID of the BriefcaseItemModel.
    :param dao: DAO for Briefcase models.
    """
    return await dao.get_briefcase_item_model(item_id)


@router.get("/{briefcase_id}/items/", response_model=List[BriefcaseItemDTO])
async def get_briefcase_items(
    briefcase_id: int,
    dao: BriefcaseDAO = Depends(),
) -> List[BriefcaseItemModel]:
    """
    Retrieve all items in a briefcase from the database.

    :param briefcase_id: ID of the BriefcaseModel.
    :param dao: DAO for Briefcase models.
    :return: List of BriefcaseItemModel objects.
    """
    return await dao.get_all_briefcase_items()


@router.post("/{briefcase_id}/items/")
async def create_briefcase_item_model(
    briefcase_id: int,
    new_item: BriefcaseItemInputDTO,  # Assuming you have a DTO for creating items
    dao: BriefcaseDAO = Depends(),
) -> None:
    """
    Create a new item in a specific briefcase.

    :param briefcase_id: ID of the BriefcaseModel.
    :param new_item: New BriefcaseItemModel object data.
    :param dao: DAO for Briefcase models.
    """
    await dao.create_briefcase_item_model(
        count=new_item.count,
        dividends=new_item.dividends,
        company_id=new_item.company.id,
        strategy_id=new_item.strategy.id if new_item.strategy else None,
        briefcase_id=briefcase_id
    )


@router.put("/items/{item_id}")
async def update_briefcase_item(
    item_id: int,
    updated_item: BriefcaseItemInputDTO,  # Assuming DTO for updating items
    dao: BriefcaseDAO = Depends(),
) -> None:
    """
    Update a specific item in a briefcase.

    :param item_id: ID of the BriefcaseItemModel to update.
    :param updated_item: Updated BriefcaseItemModel object data.
    :param dao: DAO for Briefcase models.
    """
    # Similar to creation, you'll need to pass the updated attributes to update_briefcase_item_model
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
