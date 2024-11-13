import logging

from server.src.schemas.ta import (
    TAStartGenerateMessage,
    PeriodEnum,
    TAMessageResponse,
    TAMessageStatus,
)
from fastapi import APIRouter

from server.src.auth import CurrentUser
from server.src.worker.tasks import start_generate_task

router = APIRouter()


@router.post("/")
async def run_generate_ts_decisions(
    current_user: CurrentUser,
) -> TAMessageResponse:
    message = TAStartGenerateMessage(
        user_id=current_user.id, period=PeriodEnum.DAY, companies=[]
    )
    payload_str = str(message.model_dump_json())
    result = start_generate_task.delay(payload_str)

    res_message = TAMessageResponse(id=result.id, status=result.status)
    logging.info(f"********* Run generate result: {res_message}")

    return res_message


@router.get("/{task_id}")
def get_task_status(task_id: str) -> TAMessageStatus:
    task = start_generate_task.AsyncResult(task_id)
    logging.info(f"********* Get task result: {str(task)}")

    response = TAMessageStatus(id=task.id, status=task.status, result=task.result)
    logging.info(f"********* Get task message: {str(response)}")

    return response
