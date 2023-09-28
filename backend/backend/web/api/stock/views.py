from typing import List

from fastapi import APIRouter, Depends

from backend.db.dao.stock import StockDAO
from backend.db.models.stocks import StockModel
from backend.web.api.stock.scheme import (StockModelDTO, StockModelInputDTO)

router = APIRouter()


@router.get("/", response_model=List[StockModelDTO])
async def get_user_models(
    limit: int = 10,
    offset: int = 0,
    stock_dao: StockDAO = Depends(),
) -> List[StockModel]:
    """
    Retrieve all stock objects from the database.

    :param stock_dao: DAO for stock models.
    :param limit: limit of stock objects, defaults to 10.
    :param offset: offset of stock objects, defaults to 0.
    :return: list of stock objects from database.
    """
    return await stock_dao.get_all_stocks(limit=limit, offset=offset)


@router.post("/")
async def create_stock_model(
    new_stock_object: StockModelInputDTO,
    stock_dao: StockDAO = Depends(),
) -> None:
    """
    Creates stock model in the database.

    :param new_stock_object: new stock model item.
    :param stock_dao: DAO for stock models.
    """
    await stock_dao.create_stock_model(
        tiker=new_stock_object.tiker,
        type=new_stock_object.type
    )

@router.post("/batch")
async def create_stock_batch_models(
    new_stocks_list: List[StockModelInputDTO],
    stock_dao: StockDAO = Depends(),
) -> None:
    """
    Creates stocks models in the database.

    :param new_stocks_list: new stocks model items.
    :param stock_dao: DAO for stock models.
    """

    await stock_dao.create_stocks_models(
        list(map(lambda s: StockModel(tiker=s.tiker, type=s.type), new_stocks_list))
    )


@router.delete("/{stock_id}", status_code=204)
async def delete_stock_model(
    stock_id: int,
    stock_dao: StockDAO = Depends(),
) -> None:
    """
    Delete stock model from the database.
    :param stock_dao:
    :param stock_id:
    """

    await stock_dao.delete_stock_model(stock_id)
