from typing import List

from backend.app.db.dao.strategies import StrategiesDAO
from backend.app.db.models.company import StrategyModel
from backend.app.api.strategy.scheme import StrategiesDTO, StrategiesInputDTO
from backend.app.auth import CurrentUser, check_owner_or_superuser
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/", response_model=List[StrategiesDTO])
async def get_strategies(
    current_user: CurrentUser,
    dao: StrategiesDAO = Depends(),
) -> List[StrategyModel]:
    return await dao.get_all_strategies_model(current_user.id)


@router.get("/{strategy_id}", response_model=StrategiesDTO)
async def get_strategy(
    strategy_id: int,
    current_user: CurrentUser,
    dao: StrategiesDAO = Depends(),
) -> StrategyModel:
    exist_strategy = await dao.get_strategy_model(strategy_id)
    await check_owner_or_superuser(exist_strategy.user_id, current_user)
    return exist_strategy


@router.post("/")
async def create_strategy(
    new_strategy_object: StrategiesInputDTO,
    current_user: CurrentUser,
    dao: StrategiesDAO = Depends(),
) -> None:
    return await dao.create_strategy_model(
        name=new_strategy_object.name,
        description=new_strategy_object.description,
        user_id=current_user.id,
    )


@router.put("/{strategy_id}")
async def update_strategy(
    strategy_id: int,
    updated_strategy: StrategiesInputDTO,
    current_user: CurrentUser,
    dao: StrategiesDAO = Depends(),
) -> None:
    exist_strategy = await dao.get_strategy_model(strategy_id)
    await check_owner_or_superuser(exist_strategy.user_id, current_user)

    return await dao.update_strategy_model(
        strategy_id,
        name=updated_strategy.name,
        description=updated_strategy.description,
    )


@router.delete("/{strategy_id}", status_code=204)
async def delete_strategy(
    strategy_id: int,
    current_user: CurrentUser,
    dao: StrategiesDAO = Depends(),
) -> None:
    exist_strategy = await dao.get_strategy_model(strategy_id)
    await check_owner_or_superuser(exist_strategy.user_id, current_user)

    await dao.delete_strategy_model(strategy_id)
