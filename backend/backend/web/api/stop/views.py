from fastapi import APIRouter, Depends

from backend.db.dao.stops import StopsDAO
from backend.web.api.stop.scheme import StopInputDTO

router = APIRouter()


@router.post("/")
async def add_company_stop_model(
    new_stop: StopInputDTO,
    dao: StopsDAO = Depends(),
) -> None:
    """
    Creates stop models in the database.
    :param dao:
    :param new_stop:
    """

    await dao.add_stop_model(
        company_id=new_stop.company_id, period=new_stop.period, value=new_stop.value
    )


@router.delete("/{stop_id}", status_code=204)
async def delete_company_stop_model(
    stop_id: int,
    dao: StopsDAO = Depends(),
) -> None:
    """
    Delete company model from the database.
    :param dao:
    :param stop_id:
    """

    await dao.delete_company_stop_model(stop_id)

