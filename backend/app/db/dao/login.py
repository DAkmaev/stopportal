from datetime import timedelta


from backend.app.db.dao.user import UserDAO
from backend.app.db.db import get_session
from backend.app.settings import settings
from backend.app.schemas.login import Token
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import security


class LoginDAO:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def authenticate(self, username: str, password: str) -> Token:
        user_dao = UserDAO(self.session)
        user = await user_dao.authenticate(username, password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        elif not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        return Token(
            access_token=security.create_access_token(
                user.id,
                expires_delta=access_token_expires,
            ),
        )
