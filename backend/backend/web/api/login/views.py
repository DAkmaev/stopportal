from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.db.dao.login import LoginDAO
from backend.web.api.login.schema import Token
from backend.web.api.user.schema import UserModelDTO
from backend.web.deps import CurrentUser

router = APIRouter()


@router.post("/access-token")
async def login_access_token(
    dao: LoginDAO = Depends(),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    token = await dao.authenticate(form_data.username, form_data.password)
    return token


@router.post("/test-token", response_model=UserModelDTO)
async def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return current_user

# @router.post("/password-recovery/{email}")
# def recover_password(email: str, session: SessionDep) -> Message:
#     """
#     Password Recovery
#     """
#     user = crud.get_user_by_email(session=session, email=email)
#
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the system.",
#         )
#     password_reset_token = generate_password_reset_token(email=email)
#     send_reset_password_email(
#         email_to=user.email, email=email, token=password_reset_token
#     )
#     return Message(message="Password recovery email sent")
#
#
# @router.post("/reset-password/")
# def reset_password(session: SessionDep, body: NewPassword) -> Message:
#     """
#     Reset password
#     """
#     email = verify_password_reset_token(token=body.token)
#     if not email:
#         raise HTTPException(status_code=400, detail="Invalid token")
#     user = crud.get_user_by_email(session=session, email=email)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the system.",
#         )
#     elif not user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     hashed_password = get_password_hash(password=body.new_password)
#     user.hashed_password = hashed_password
#     session.add(user)
#     session.commit()
#     return Message(message="Password updated successfully")
