from datetime import datetime
from typing import List

from app.db.dao.common import update_registry_field
from app.db.dependencies import get_db_session
from app.db.models.briefcase import (
    BriefcaseModel,
    BriefcaseRegistryModel,
    CurrencyEnum,
    RegistryOperationEnum,
)
from app.db.models.company import CompanyModel, StrategyModel
from app.db.models.user import UserModel
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BriefcaseDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_briefcase_model(
        self,
        user_id: int,
        fill_up: float = None,
    ) -> BriefcaseModel:
        user = await self.session.get(UserModel, user_id)
        briefcase = BriefcaseModel(fill_up=fill_up, user=user)
        self.session.add(briefcase)
        return briefcase

    async def get_all_briefcases(
        self,
        user_id: int,
        limit: int = 10000,
        offset: int = 0,
    ) -> List[BriefcaseModel]:
        raw_briefcases = await self.session.execute(
            select(BriefcaseModel)
            .where(BriefcaseModel.user_id == user_id)
            .limit(limit)
            .offset(offset),
        )
        return list(raw_briefcases.scalars().fetchall())

    async def get_briefcase_model(self, briefcase_id: int) -> BriefcaseModel:
        briefcase = await self.session.get(BriefcaseModel, briefcase_id)

        if not briefcase:
            raise HTTPException(status_code=404, detail="Briefcase not found")

        return briefcase

    async def update_briefcase_model(
        self,
        briefcase_id: int,
        fill_up: float,
    ) -> BriefcaseModel:
        briefcase = await self.get_briefcase_model(briefcase_id)
        briefcase.fill_up = fill_up
        return briefcase

    async def delete_briefcase_model(self, briefcase_id: int) -> None:
        briefcase = await self.get_briefcase_model(briefcase_id)
        await self.session.delete(briefcase)

    async def get_all_briefcase_registry(  # noqa:  WPS211
        self,
        briefcase_id: int,
        limit: int = 100,
        offset: int = 0,
        date_from: datetime = None,
        date_to: datetime = None,
    ) -> List[BriefcaseRegistryModel]:
        query = select(BriefcaseRegistryModel).filter_by(briefcase_id=briefcase_id)

        if date_from:
            query = query.where(BriefcaseRegistryModel.created_date > date_from)

        if date_to:
            query = query.where(BriefcaseRegistryModel.created_date < date_to)

        raw_briefcase_registry = await self.session.execute(
            query.limit(limit)
            .offset(offset)
            .order_by(BriefcaseRegistryModel.created_date.desc()),
        )
        return list(raw_briefcase_registry.scalars().fetchall())

    async def get_briefcase_registry_model(
        self,
        registry_id: int,
    ) -> BriefcaseRegistryModel:
        registry_item = await self.session.get(BriefcaseRegistryModel, registry_id)

        if not registry_item:
            raise HTTPException(status_code=404, detail="Briefcase registry not found")

        return registry_item

    async def create_briefcase_registry_model(  # noqa:  WPS211
        self,
        count: int,
        amount: float,
        company_id: int,
        briefcase_id: int,
        operation: RegistryOperationEnum,
        strategy_id: int = None,
        price: float = None,
        currency: CurrencyEnum = CurrencyEnum.RUB,
        created_date: datetime = datetime.now(),
    ) -> BriefcaseRegistryModel:
        briefcase = await self.session.get(BriefcaseModel, briefcase_id)
        if not briefcase:
            raise HTTPException(status_code=404, detail="Портфель не найдена")

        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        registry = BriefcaseRegistryModel(
            count=count,
            amount=amount,
            company=company,
            briefcase=briefcase,
            operation=operation,
            currency=currency,
            created_date=created_date,
            price=price,
        )
        if strategy_id:
            strategy = await self.session.get(StrategyModel, strategy_id)
            registry.strategy = strategy

        if not created_date:
            registry.created_date = datetime.now()

        self.session.add(registry)
        return registry

    async def update_briefcase_registry_model(
        self,
        registry_id: int,
        updated_fields: dict,
    ) -> BriefcaseRegistryModel:
        registry_item = await self.get_briefcase_registry_model(registry_id)
        if not registry_item:
            raise HTTPException(status_code=404, detail="Запись не найдена")

        await update_registry_field(
            self.session,
            CompanyModel,
            "company",
            updated_fields,
            registry_item,
            "Компания не найдена",
        )
        await update_registry_field(
            self.session,
            StrategyModel,
            "strategy",
            updated_fields,
            registry_item,
            "Стратегия не найдена",
        )

        # Update other fields if specified and allowed
        for field, value in updated_fields.items():
            if field in registry_item.__dict__ and value is not None:
                setattr(registry_item, field, value)

        return registry_item

    async def delete_briefcase_registry_model(self, registry_id: int) -> None:
        registry_item = await self.get_briefcase_registry_model(registry_id)
        await self.session.delete(registry_item)
