from typing import Annotated

from app.db.dependencies import get_db_session
from app.db.models.user import UserModel
from app.settings import settings
from app.web.api.login.schema import TokenPayload
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_str}/login",
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(
    session: AsyncSession = Depends(get_db_session),
    token: str = Depends(reusable_oauth2),
) -> UserModel:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await session.get(UserModel, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[UserModel, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> UserModel:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return current_user


CurrentAdminUser = Annotated[UserModel, Depends(get_current_active_superuser)]
