from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dao.common import update_registry_field
from app.db.dependencies import get_db_session
from fastapi import Depends, HTTPException
from typing import List

from app.db.models.briefcase import (
    BriefcaseModel,
    BriefcaseItemModel,
    BriefcaseRegistryModel,
    CurrencyEnum,
    RegistryOperationEnum,
)
from app.db.models.company import CompanyModel, StrategyModel


class BriefcaseDAO:
    """Class for accessing briefcases and briefcase_items tables."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_briefcase_model(self, fill_up: float = None) -> BriefcaseModel:
        """
        Add a single briefcase to the session.

        :param fill_up: Amount to fill up the briefcase.
        """
        briefcase = BriefcaseModel(fill_up=fill_up)
        self.session.add(briefcase)
        return briefcase

    async def create_briefcase_item_model(
        self,
        count: int,
        briefcase_id: int,
        company_id: int,
        strategy_id: int = None,
        dividends: float = None,
    ) -> BriefcaseItemModel:
        """
        Add a single briefcase item to the session.

        :param briefcase_id:
        :param count: Number of items in the briefcase.
        :param dividends: Dividends for the briefcase item.
        :param company_id: ID of the associated company.
        :param strategy_id: ID of the associated strategy.
        """
        briefcase = await self.session.get(BriefcaseModel, briefcase_id)
        if not briefcase:
            raise HTTPException(status_code=404, detail="Портфель не найдена")

        company = await self.session.get(CompanyModel, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Компания не найдена")

        briefcase_item = BriefcaseItemModel(
            count=count, dividends=dividends, company=company, briefcase_id=briefcase.id
        )
        if strategy_id:
            strategy = await self.session.get(StrategyModel, strategy_id)
            briefcase_item.strategy = strategy

        self.session.add(briefcase_item)
        return briefcase_item

    async def get_all_briefcases(
        self, limit: int = 10000, offset: int = 0
    ) -> List[BriefcaseModel]:
        """
        Get all briefcase models with limit/offset pagination.

        :param limit: Limit of briefcases.
        :param offset: Offset of briefcases.
        :return: List of briefcase models.
        """
        raw_briefcases = await self.session.execute(
            select(BriefcaseModel).limit(limit).offset(offset)
        )
        return list(raw_briefcases.scalars().fetchall())

    async def get_briefcase_model(self, briefcase_id: int) -> BriefcaseModel:
        """
        Get briefcase model by ID.

        :param briefcase_id: ID of the briefcase.
        :return: Briefcase model.
        """
        briefcase = await self.session.get(BriefcaseModel, briefcase_id)

        if not briefcase:
            raise HTTPException(status_code=404, detail="Briefcase not found")

        return briefcase

    async def get_all_briefcase_items(self) -> List[BriefcaseItemModel]:
        """
        Get all briefcase item models with limit/offset pagination.

        :return: List of briefcase item models.
        """
        raw_briefcase_items = await self.session.execute(select(BriefcaseItemModel))
        return list(raw_briefcase_items.scalars().fetchall())

    async def get_briefcase_item_model(
        self, briefcase_item_id: int
    ) -> BriefcaseItemModel:
        """
        Get briefcase item model by ID.

        :param briefcase_item_id: ID of the briefcase item.
        :return: Briefcase item model.
        """
        briefcase_item = await self.session.get(BriefcaseItemModel, briefcase_item_id)

        if not briefcase_item:
            raise HTTPException(status_code=404, detail="Briefcase item not found")

        return briefcase_item

    async def get_briefcase_items_by_company(
        self, company_id: int
    ) -> List[BriefcaseItemModel]:
        """
        Get briefcase item models by company ID.

        :param company_id: ID of the company.
        :return: List of briefcase item models.
        """
        raw_briefcase_items = await self.session.execute(
            select(BriefcaseItemModel).filter_by(company_id=company_id)
        )
        return list(raw_briefcase_items.scalars().fetchall())

    async def get_briefcase_items_by_briefcase(
        self, briefcase_id: int
    ) -> List[BriefcaseItemModel]:
        """
        Get briefcase item models by briefcase ID.

        :param briefcase_id: ID of the briefcase.
        :return: List of briefcase item models.
        """
        raw_briefcase_items = await self.session.execute(
            select(BriefcaseItemModel).filter_by(briefcase_id=briefcase_id)
        )
        return list(raw_briefcase_items.scalars().fetchall())

    async def update_briefcase_model(
        self, briefcase_id: int, fill_up: float
    ) -> BriefcaseModel:
        """
        Update briefcase model in the session.

        :param briefcase_id: ID of the briefcase.
        :param fill_up: Updated fill-up amount.
        :return: Updated briefcase model.
        """
        briefcase = await self.get_briefcase_model(briefcase_id)
        briefcase.fill_up = fill_up
        return briefcase

    async def update_briefcase_item_model(
        self, briefcase_item_id: int, count: int, dividends: float
    ) -> BriefcaseItemModel:
        """
        Update briefcase item model in the session.

        :param briefcase_item_id: ID of the briefcase item.
        :param count: Updated count of items.
        :param dividends: Updated dividends for the item.
        :return: Updated briefcase item model.
        """
        briefcase_item = await self.get_briefcase_item_model(briefcase_item_id)
        briefcase_item.count = count
        briefcase_item.dividends = dividends
        return briefcase_item

    async def delete_briefcase_model(self, briefcase_id: int) -> None:
        """
        Delete briefcase model in the session.

        :param briefcase_id: ID of the briefcase to delete.
        """
        briefcase = await self.get_briefcase_model(briefcase_id)
        await self.session.delete(briefcase)

    async def delete_briefcase_item_model(self, briefcase_item_id: int) -> None:
        """
        Delete briefcase item model in the session.

        :param briefcase_item_id: ID of the briefcase item to delete.
        """
        briefcase_item = await self.get_briefcase_item_model(briefcase_item_id)
        await self.session.delete(briefcase_item)

    async def get_all_briefcase_registry(
        self,
        briefcase_id: int,
        limit: int = 100,
        offset: int = 0,
        date_from: datetime = None,
        date_to: datetime = None,
    ) -> List[BriefcaseRegistryModel]:
        """
        Get all briefcase registry models with limit/offset pagination.

        :param date_to:
        :param date_from:
        :param briefcase_id:
        :param limit: Limit of briefcase items.
        :param offset: Offset of briefcase items.
        :return: List of briefcase item models.
        """
        query = select(BriefcaseRegistryModel).filter_by(briefcase_id=briefcase_id)

        if date_from:
            query = query.where(BriefcaseRegistryModel.created_date > date_from)

        if date_to:
            query = query.where(BriefcaseRegistryModel.created_date < date_to)

        raw_briefcase_registry = await self.session.execute(
            query.limit(limit)
            .offset(offset)
            .order_by(BriefcaseRegistryModel.created_date.desc())
        )
        return list(raw_briefcase_registry.scalars().fetchall())

    async def get_briefcase_registry_model(
        self, registry_id: int
    ) -> BriefcaseRegistryModel:
        """
        Get briefcase registry model by ID.

        :param registry_id: ID of the briefcase registry.
        :return: Briefcase registry model.
        """
        registry_item = await self.session.get(BriefcaseRegistryModel, registry_id)

        if not registry_item:
            raise HTTPException(status_code=404, detail="Briefcase registry not found")

        return registry_item

    async def create_briefcase_registry_model(
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
        """
        Add a single briefcase registry to the session.

        :param created_date:
        :param currency:
        :param price:
        :param operation:
        :param amount:
        :param briefcase_id:
        :param count: Number of items in the briefcase.
        :param company_id: ID of the associated company.
        :param strategy_id: ID of the associated strategy.
        """
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
        self, registry_id: int, updated_fields: dict
    ) -> BriefcaseRegistryModel:
        """
        Update briefcase item model in the session.

        :param updated_fields: Dict
        :param registry_id: int
        :return: Updated briefcase registry model.
        """
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
            if hasattr(registry_item, field) and value is not None:
                setattr(registry_item, field, value)

        return registry_item

    async def delete_briefcase_registry_model(self, registry_id: int) -> None:
        """
        Delete briefcase registry model in the session.

        :param registry_id: ID of the briefcase registry to delete.
        """
        registry_item = await self.get_briefcase_registry_model(registry_id)
        await self.session.delete(registry_item)
