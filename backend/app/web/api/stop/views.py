from app.db.dao.stops import StopsDAO
from app.web.api.stop.scheme import StopDTO, StopInputDTO
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/")
async def add_stop_model(
    new_stop: StopInputDTO,
    dao: StopsDAO = Depends(),
) -> None:
    await dao.add_stop_model(
        company_id=new_stop.company_id, period=new_stop.period, value=new_stop.value,
    )


@router.delete("/{stop_id}", status_code=204)
async def delete_stop_model(
    stop_id: int,
    dao: StopsDAO = Depends(),
) -> None:
    await dao.delete_stop_model(stop_id)


@router.put("/")
async def update_stop_model(
    updated_stop: StopDTO,
    dao: StopsDAO = Depends(),
) -> None:
    await dao.update_stop_model(updated_stop.model_dump())
