from datetime import timedelta

from app.core import security
from app.db.dao.user import UserDAO
from app.db.dependencies import get_db_session
from app.settings import settings
from app.web.api.login.schema import Token
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


class LoginDAO:
    """Class for accessing user table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
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
                user.id, expires_delta=access_token_expires
            )
        )
