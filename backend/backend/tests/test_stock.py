import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.db.dao.stock import StockDAO
from backend.db.models.stocks import StockModel


async def create_test_stock(
    dbsession: AsyncSession,
    need_add_stop: bool = False
) -> StockModel:
    dao = StockDAO(dbsession)
    tiker_name = uuid.uuid4().hex
    await dao.create_stock_model(tiker_name, "MOEX")

    stocks = await dao.filter(tiker=tiker_name)

    if need_add_stop:
        await dao.add_stop_model(stocks[0].id, "D", 100)
        stocks = await dao.filter(tiker=tiker_name)

    return stocks[0]

@pytest.mark.anyio
async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests stock instance creation."""
    url = fastapi_app.url_path_for("create_stock_model")
    tiker_name = uuid.uuid4().hex
    response = await client.post(
        url,
        json={
            "tiker": tiker_name,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    dao = StockDAO(dbsession)
    instances = await dao.filter(tiker=tiker_name)
    assert instances[0].tiker == tiker_name


@pytest.mark.anyio
async def test_getting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests stock instance retrieval."""
    stock = await create_test_stock(dbsession)

    url = fastapi_app.url_path_for("get_stock_models")
    response = await client.get(url)
    stocks = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(stocks) == 1
    assert stocks[0]["tiker"] == stock.tiker


@pytest.mark.anyio
async def test_stop_adding(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests stock instance creation."""
    stock = await create_test_stock(dbsession)

    url = fastapi_app.url_path_for("add_stock_stop_model", stock_id=stock.id)
    response = await client.post(
        url,
        json={
            "period": "D",
            "value": 100
        },
    )
    assert response.status_code == status.HTTP_200_OK

    dao = StockDAO(dbsession)
    stock_upd = await dao.get_stock_model(stock.id)
    assert len(stock_upd.stops) == 1
    assert stock_upd.stops[0].value == 100
    assert stock_upd.stops[0].period == 'D'


@pytest.mark.anyio
async def test_stop_deleting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests stock stop instance deleting."""
    stock = await create_test_stock(dbsession, True)
    stop_id = stock.stops[0].id

    url = fastapi_app.url_path_for("delete_stock_stop_model",
                                   stock_id=stock.id, stop_id=stop_id)
    response = await client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    dao = StockDAO(dbsession)
    stop = await dao.get_stock_stop_model(stop_id)
    assert stop is None
