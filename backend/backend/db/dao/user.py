from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import get_password_hash
from backend.db.dependencies import get_db_session
from fastapi import Depends
from typing import List, Optional

from backend.db.models.user import UserModel


class UserDAO:
    """Class for accessing user table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_user_model(self, name: str, email: str, password: str, is_superuser: bool, is_active: bool) -> None:
        """
        Add single user to session.

        :param name: name of a user.
        :param email
        :param is_superuser: is superuser
        """
        self.session.add(UserModel(
            name=name,
            email=email,
            hashed_password=get_password_hash(password),
            is_superuser=is_superuser,
            is_active=is_active
        ))

    async def get_all_users(self, limit: int, offset: int) -> List[UserModel]:
        """
        Get all user models with limit/offset pagination.

        :param limit: limit of dummies.
        :param offset: offset of dummies.
        :return: stream of users.
        """
        raw_users = await self.session.execute(
            select(UserModel).limit(limit).offset(offset),
        )

        return list(raw_users.scalars().fetchall())

    async def get_user(self, id: int) -> UserModel:
        """
        Get user models by id.

        :param id: user id.
        :return: user.
        """
        user = await self.session.execute(
            select(UserModel).where(id == id)
        )

        return user.scalars().one_or_none()

    async def filter(
        self,
        name: Optional[str] = None,
    ) -> List[UserModel]:
        """
        Get specific user model.

        :param name: name of user instance.
        :return: user models.
        """
        query = select(UserModel)
        if name:
            query = query.where(UserModel.name == name)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
