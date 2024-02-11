from typing import Any

from app.db.dao.login import LoginDAO
from app.web.api.auth.schema import UserModelDTO
from app.web.api.login.schema import Token
from app.web.deps import CurrentUser
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/access-token")
async def login_access_token(
    dao: LoginDAO = Depends(),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    return await dao.authenticate(form_data.username, form_data.password)


@router.post("/test-token", response_model=UserModelDTO)
async def test_token(current_user: CurrentUser) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return current_user
