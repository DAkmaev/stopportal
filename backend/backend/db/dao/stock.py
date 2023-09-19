from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.dependencies import get_db_session
from fastapi import Depends, HTTPException
from typing import List, Optional

from backend.db.models.stocks import StockModel


class StockDAO:
    """Class for accessing stock table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_stock_model(self, tiker: str, type: str) -> None:
        """
        Add single stock to session.

        :param tiker: tiker of a stock.
        :param type: type of stock:  MOEX or YAHOO.
        """
        self.session.add(StockModel(
            tiker=tiker,
            type=type
        ))

    async def create_stocks_models(self, items: List[StockModel]) -> None:
        """
        Add multiple stocks to session.

        :param items:
        """
        self.session.add_all(items)

    async def delete_stock_model(self, stock_id: int) -> None:
        """
        Delete stock in session.
        :param stock_id:
        """
        stock = await self.session.get(StockModel, stock_id)
        if not stock:
            raise HTTPException(status_code=404, detail="Акция не найдена")

        await self.session.delete(stock)


    async def get_all_stocks(self, limit: int = 100, offset: int = 0) -> List[StockModel]:
        """
        Get all stocks models with limit/offset pagination.

        :param limit: limit of dummies.
        :param offset: offset of dummies.
        :return: stream of stocks.
        """
        raw_stocks = await self.session.execute(
            select(StockModel).limit(limit).offset(offset),
        )

        return list(raw_stocks.scalars().fetchall())

    async def get_stock(self, id: int) -> StockModel:
        """
        Get stock models by id.

        :param id: stock id.
        :return: stock.
        """
        stock = await self.session.execute(
            select(StockModel).where(id == id)
        )

        return stock.scalars().one_or_none()

    async def filter(
        self,
        tiker: Optional[str] = None,
    ) -> List[StockModel]:
        """
        Get specific stock model.

        :param tiker: tiker of stock instance.
        :return: stock models.
        """
        query = select(StockModel)
        if tiker:
            query = query.where(StockModel.name == tiker)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
