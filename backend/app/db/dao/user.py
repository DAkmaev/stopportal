from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.db.dependencies import get_db_session
from fastapi import Depends, HTTPException
from typing import List, Optional, Any

from app.db.models.user import UserModel


class UserDAO:
    """Class for accessing user table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_user_model(
        self,
        name: str,
        email: str,
        password: str,
        is_superuser: bool = False,
        is_active: bool = True,
    ) -> UserModel:
        """
        Add single user to session.

        :param name: name of a user.
        :param email
        :param is_superuser: is superuser
        """
        user = UserModel(
            name=name,
            email=email,
            hashed_password=get_password_hash(password),
            is_superuser=is_superuser,
            is_active=is_active,
        )

        self.session.add(user)
        return user

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
        user = await self.session.get(UserModel, id)

        return user

    async def get_user_by_email(self, email: str) -> UserModel:
        rows = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return rows.scalars().one_or_none()

    async def get_user_by_name(self, name: str) -> UserModel:
        rows = await self.session.execute(
            select(UserModel).where(UserModel.name == name)
        )
        return rows.scalars().one_or_none()

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

    async def authenticate(self, name: str, password: str) -> UserModel | None:
        rows = await self.session.execute(
            select(UserModel).where(UserModel.name == name)
        )
        user = rows.scalars().one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def update(self, user_id: int, updated_fields: dict) -> UserModel:
        user = await self.get_user(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        password = updated_fields.pop("password", None)
        if password is not None:
            updated_fields["hashed_password"] = get_password_hash(password)

        # Update other fields if specified and allowed
        for field, value in updated_fields.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)

        return user
