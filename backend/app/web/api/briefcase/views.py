from datetime import datetime
from typing import List

from app.db.dao.briefcases import BriefcaseDAO
from app.db.models.briefcase import BriefcaseModel, BriefcaseRegistryModel
from app.services.briefcase_service import BriefcaseService
from app.web.api.briefcase.scheme import (
    BriefcaseDTO,
    BriefcaseInputDTO,
    BriefcaseRegistryDTO,
    BriefcaseRegistryInputDTO,
)
from app.web.deps import CurrentUser, check_owner_or_superuser
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get("/{briefcase_id}", response_model=BriefcaseDTO)
async def get_briefcase_model(
    briefcase_id: int,
    current_user: CurrentUser,
    dao: BriefcaseDAO = Depends(),
) -> BriefcaseModel:
    exist_briefcase = await dao.get_briefcase_model(briefcase_id)
    await check_owner_or_superuser(exist_briefcase.user_id, current_user)

    return exist_briefcase


@router.get("/", response_model=List[BriefcaseDTO])
async def get_briefcase_models(
    current_user: CurrentUser,
    limit: int = 100,
    offset: int = 0,
    dao: BriefcaseDAO = Depends(),
) -> List[BriefcaseModel]:
    return await dao.get_all_briefcases(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.post("/")
async def create_briefcase_model(
    new_briefcase_object: BriefcaseInputDTO,
    current_user: CurrentUser,
    dao: BriefcaseDAO = Depends(),
) -> None:
    await dao.create_briefcase_model(
        user_id=current_user.id,
        fill_up=new_briefcase_object.fill_up,
    )


@router.put("/{briefcase_id}")
async def update_briefcase_model(
    briefcase_id: int,
    updated_briefcase: BriefcaseInputDTO,
    current_user: CurrentUser,
    dao: BriefcaseDAO = Depends(),
) -> None:
    exist_briefcase = await dao.get_briefcase_model(briefcase_id)
    await check_owner_or_superuser(exist_briefcase.user_id, current_user)

    await dao.update_briefcase_model(briefcase_id, updated_briefcase.fill_up)


@router.delete("/{briefcase_id}", status_code=204)
async def delete_briefcase_model(
    briefcase_id: int,
    current_user: CurrentUser,
    dao: BriefcaseDAO = Depends(),
) -> None:
    exist_briefcase = await dao.get_briefcase_model(briefcase_id)
    await check_owner_or_superuser(exist_briefcase.user_id, current_user)

    await dao.delete_briefcase_model(briefcase_id)


@router.get("/{briefcase_id}/registry/{item_id}", response_model=BriefcaseRegistryDTO)
async def get_briefcase_registry(
    briefcase_id: int,
    item_id: int,
    current_user: CurrentUser,
    dao: BriefcaseDAO = Depends(),
) -> BriefcaseRegistryModel:
    exist_briefcase = await dao.get_briefcase_model(briefcase_id)
    await check_owner_or_superuser(exist_briefcase.user_id, current_user)

    exist_item = await dao.get_briefcase_registry_model(item_id)
    if exist_item.briefcase.id != briefcase_id:
        raise HTTPException(
            status_code=400,
            detail="The item_id doesn't match briefcase",
        )

    return exist_item


@router.get("/{briefcase_id}/registry/", response_model=List[BriefcaseRegistryDTO])
async def get_briefcase_registries(  # noqa: WPS211
    briefcase_id: int,
    current_user: CurrentUser,
    dao: BriefcaseDAO = Depends(),
    limit: int = 100000,
    offset: int = 0,
    date_from: str = None,
    date_to: str = None,
) -> List[BriefcaseRegistryModel]:
    exist_briefcase = await dao.get_briefcase_model(briefcase_id)
    await check_owner_or_superuser(exist_briefcase.user_id, current_user)

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
    current_user: CurrentUser,
    new_item: BriefcaseRegistryInputDTO,  # Assuming you have a DTO for creating items
    dao: BriefcaseDAO = Depends(),
    brief_service: BriefcaseService = Depends(),
) -> None:
    exist_briefcase = await dao.get_briefcase_model(briefcase_id)
    await check_owner_or_superuser(exist_briefcase.user_id, current_user)

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
    await brief_service.recalculate_share(
        company_id=new_item.company.id,
        briefcase_id=briefcase_id,
    )


@router.put("/{briefcase_id}/registry/{item_id}")
async def update_briefcase_registry(  # noqa:  WPS211
    briefcase_id: int,
    item_id: int,
    current_user: CurrentUser,
    updated_item: BriefcaseRegistryInputDTO,
    dao: BriefcaseDAO = Depends(),
    brief_service: BriefcaseService = Depends(),
) -> None:
    exist_briefcase = await dao.get_briefcase_model(briefcase_id)
    await check_owner_or_superuser(exist_briefcase.user_id, current_user)

    exist_item = await dao.get_briefcase_registry_model(item_id)
    if exist_item.briefcase.id != briefcase_id:
        raise HTTPException(
            status_code=400,
            detail="The item_id doesn't match briefcase",
        )

    await dao.update_briefcase_registry_model(
        registry_id=item_id,
        updated_fields=updated_item.model_dump(),
    )

    await brief_service.recalculate_share(
        company_id=exist_item.company_id,
        briefcase_id=briefcase_id,
    )


@router.delete("/{briefcase_id}/registry/{item_id}", status_code=204)
async def delete_briefcase_registry(
    briefcase_id: int,
    item_id: int,
    current_user: CurrentUser,
    dao: BriefcaseDAO = Depends(),
    brief_service: BriefcaseService = Depends(),
) -> None:
    exist_briefcase = await dao.get_briefcase_model(briefcase_id)
    await check_owner_or_superuser(exist_briefcase.user_id, current_user)

    exist_item = await dao.get_briefcase_registry_model(item_id)
    if exist_item.briefcase.id != briefcase_id:
        raise HTTPException(
            status_code=400,
            detail="The item_id doesn't match briefcase",
        )

    await dao.delete_briefcase_registry_model(item_id)
    await brief_service.recalculate_share(
        company_id=exist_item.company_id,
        briefcase_id=briefcase_id,
    )
