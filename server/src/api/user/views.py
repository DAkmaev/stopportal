import logging
from typing import List

from server.src.db.dao.user import UserDAO
from server.src.db.models.user import UserModel
from server.src.schemas.user import UserModelDTO, UserModelInputDTO
from server.src.auth import CurrentUser
from fastapi import APIRouter, Depends

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/me", response_model=UserModelDTO)
async def read_user_me(current_user: CurrentUser) -> UserModelDTO:
    return current_user


@router.get("/{user_id}", response_model=UserModelDTO)
async def get_user(
    user_id: int,
    user_dao: UserDAO = Depends(),
) -> UserModel:
    return await user_dao.get_user(user_id=user_id)


@router.get("/", response_model=List[UserModelDTO])
async def get_users(
    limit: int = 10,
    offset: int = 0,
    user_dao: UserDAO = Depends(),
) -> List[UserModel]:
    return await user_dao.get_all_users(limit=limit, offset=offset)


@router.post("/")
async def create_user(
    new_user_object: UserModelInputDTO,
    user_dao: UserDAO = Depends(),
) -> None:
    await user_dao.create_user_model(
        name=new_user_object.name,
        email=new_user_object.email,
        password=new_user_object.password,
        is_superuser=new_user_object.is_superuser,
        is_active=new_user_object.is_active,
    )
