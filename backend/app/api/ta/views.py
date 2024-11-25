import logging
from typing import List

from backend.app.db.dao.ta_decisions import TADecisionDAO
from backend.app.schemas.ta import DecisionDTO
from backend.app.schemas.ta import (
    TAMessageResponse,
    TAMessageStatus,
)
from fastapi import APIRouter, Depends

from backend.app.auth import CurrentUser
from backend.app.worker.tasks import start_generate_task
from backend.app.services.ta_service import TAService

router = APIRouter()


@router.post("/")
async def run_generate_ts_decisions(
    current_user: CurrentUser,
    period: str = "All",
    send_messages: bool = False,
    update_db: bool = False,
    send_test_message: bool = False,
    ta_service: TAService = Depends(),
) -> TAMessageResponse:

    message = await ta_service.fill_send_start_generate_message(
        user_id=current_user.id,
        period=period,
        send_messages=send_messages,
        update_db=update_db,
        send_test_message=send_test_message,
    )

    result = start_generate_task.delay(str(message.model_dump_json()))
    return TAMessageResponse(id=result.id, status=result.status)


@router.get("/{task_id}")
def get_task_status(task_id: str) -> TAMessageStatus:
    task = start_generate_task.AsyncResult(task_id)
    logging.info(f"********* Get task result: {str(task)}")

    response = TAMessageStatus(id=task.id, status=task.status, result=task.result)
    logging.info(f"********* Get task message: {str(response)}")

    return response


class TADecisionDTO:
    pass


@router.get("/")
async def get_ts_decisions(stoch_dao: TADecisionDAO = Depends()) -> List[DecisionDTO]:
    decisions = await stoch_dao.get_ta_decision_models()
    return [
        DecisionDTO(
            tiker=dec.company.tiker,
            decision=dec.decision,
            last_pric=dec.last_price,
            k=dec.k,
            d=dec.d,
            period=dec.period,
        )
        for dec in decisions
    ]
