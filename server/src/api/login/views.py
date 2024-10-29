from typing import Any

from app.db.dao.login import LoginDAO
from src.schemas.user import UserModelDTO
from src.schemas.login import Token
from src.auth import CurrentAdminUser, CurrentUser
from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("")
async def login_access_token(
    dao: LoginDAO = Depends(),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    return await dao.authenticate(form_data.username, form_data.password)


@router.post("/test-token", response_model=UserModelDTO)
async def test_token(current_user: CurrentUser) -> Any:
    return current_user


@router.post("/test-admin-token", response_model=UserModelDTO)
async def test_admin_token(current_admin_user: CurrentAdminUser) -> Any:
    return current_admin_user
