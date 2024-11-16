from typing import List, Optional

from backend.app.security import get_password_hash, verify_password
from backend.app.db.db import get_session
from backend.app.db.models.user import UserModel
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserDAO:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def create_user_model(  # noqa: WPS211
        self,
        name: str,
        email: str,
        password: str,
        is_superuser: bool = False,
        is_active: bool = True,
    ) -> UserModel:
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
        raw_users = await self.session.execute(
            select(UserModel).limit(limit).offset(offset),
        )

        return list(raw_users.scalars().fetchall())

    async def get_user(self, user_id: int) -> UserModel:
        return await self.session.get(UserModel, user_id)

    async def get_user_by_email(self, email: str) -> UserModel:
        rows = await self.session.execute(
            select(UserModel).where(UserModel.email == email),
        )
        return rows.scalars().one_or_none()

    async def get_user_by_name(self, name: str) -> UserModel:
        rows = await self.session.execute(
            select(UserModel).where(UserModel.name == name),
        )
        return rows.scalars().one_or_none()

    async def filter(
        self,
        name: Optional[str] = None,
    ) -> List[UserModel]:
        query = select(UserModel)
        if name:
            query = query.where(UserModel.name == name)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

    async def authenticate(self, name: str, password: str) -> UserModel | None:
        rows = await self.session.execute(
            select(UserModel).where(UserModel.name == name),
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
            if field in user.__dict__ and value is not None:
                setattr(user, field, value)

        return user
