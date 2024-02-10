from typing import List

from fastapi import APIRouter, Depends

from app.db.dao.strategies import StrategiesDAO
from app.db.models.company import StrategyModel
from app.web.api.strategy.scheme import StrategiesDTO, StrategiesInputDTO

router = APIRouter()


@router.get("/{strategy_id}", response_model=StrategiesDTO)
async def get_strategy_model(
    strategy_id: int,
    dao: StrategiesDAO = Depends(),
) -> StrategyModel:
    """
    Retrieve Strategy by id from the database.
    """
    return await dao.get_strategy_model(strategy_id)


@router.get("/", response_model=List[StrategiesDTO])
async def get_strategy_models(
    dao: StrategiesDAO = Depends(),
) -> List[StrategyModel]:
    """
    Retrieve all strategies objects from the database.

    :param dao: DAO for strategies models.
    :param limit: limit of company objects, defaults to 10.
    :param offset: offset of company objects, defaults to 0.
    :return: list of strategies objects from database.
    """
    return await dao.get_all_strategies_model()


@router.post("/")
async def create_strategy_model(
    new_strategy_object: StrategiesInputDTO,
    dao: StrategiesDAO = Depends(),
) -> None:
    """
    Creates strategy model in the database.

    :param new_strategy_object: new strategy model item.
    :param dao: DAO for strategy models.
    """
    strategy = await dao.create_strategy_model(
        name=new_strategy_object.name,
        description=new_strategy_object.description
    )
    return strategy


@router.put("/{id}")
async def update_strategy_model(
    id: int,
    updated_strategy: StrategiesInputDTO,
    dao: StrategiesDAO = Depends(),
) -> None:
    """
    Updates strategy model in the database.

    :param id: ID of the strategy to be updated.
    :param updated_strategy: Updated strategy model item.
    :param dao: DAO for strategy models.
    """
    strategy = await dao.update_strategy_model(
        id, name=updated_strategy.name, description=updated_strategy.description
    )
    return strategy


@router.delete("/{id}", status_code=204)
async def delete_strategy_model(
    id: int,
    dao: StrategiesDAO = Depends(),
) -> None:
    """
    Delete strategy model from the database.
    :param dao:
    :param id:
    """

    await dao.delete_strategy_model(id)
