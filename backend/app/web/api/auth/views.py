from typing import List

from fastapi import APIRouter, Depends

from app.db.dao.user import UserDAO
from app.db.models.user import UserModel
from app.web.api.auth.schema import UserModelInputDTO, UserModelDTO
from app.web.deps import CurrentUser

router = APIRouter()


@router.get("/{user_id}", response_model=UserModelDTO)
async def get_user_model(
    user_id: int,
    user_dao: UserDAO = Depends(),
) -> UserModel:
    """
    Retrieve all dummy objects from the database.

    :param user_dao: DAO for user models.
    :param user_id: ID of user.
    :return: user object from database.
    """
    return await user_dao.get_user(id=user_id)


@router.get("/", response_model=List[UserModelDTO])
async def get_user_models(
    limit: int = 10,
    offset: int = 0,
    user_dao: UserDAO = Depends(),
) -> List[UserModel]:
    """
    Retrieve all dummy objects from the database.

    :param user_dao: DAO for user models.
    :param limit: limit of dummy objects, defaults to 10.
    :param offset: offset of dummy objects, defaults to 0.
    :return: list of dummy objects from database.
    """
    return await user_dao.get_all_users(limit=limit, offset=offset)


@router.post("/")
async def create_user_model(
    new_user_object: UserModelInputDTO,
    user_dao: UserDAO = Depends(),
) -> None:
    """
    Creates dummy model in the database.

    :param new_user_object: new user model item.
    :param user_dao: DAO for user models.
    """
    await user_dao.create_user_model(
        name=new_user_object.name,
        email=new_user_object.email,
        password=new_user_object.password,
        is_superuser=new_user_object.is_superuser,
        is_active=new_user_object.is_active,
    )


@router.post("/me", response_model=UserModelDTO)
async def read_user_me(current_user: CurrentUser) -> UserModelDTO:
    """
    Get current user.
    """
    return current_user
