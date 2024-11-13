import logging

from celery.result import AsyncResult
from pydantic import TypeAdapter

from server.src.schemas.ta import (
    TAStartGenerateMessage,
    PeriodEnum,
    TAMessageResponse,
    TAMessageStatus,
)
from fastapi import APIRouter, Depends

from server.src.worker.worker import celery_app
from server.src.auth import CurrentUser
from server.src.worker.tasks import start_generate_task

router = APIRouter()


# @router.get("/")
# async def get_ts_decisions(stoch_dao: TADecisionDAO = Depends()) -> List[TADecisionDTO]:
#     return await stoch_dao.get_ta_decision_models()


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
    logging.info(f"********* Result: {res_message}")

    return res_message


@router.get("/{task_id}")
def get_task_status(task_id: str) -> TAMessageStatus:
    task = start_generate_task.AsyncResult(task_id)

    response = TAMessageStatus(id=task.id, status=task.status, result=task.result)
    logging.info(f"********* Result2: {str(response)}")

    return response
    # return TAMessageStatus(
    #     id=task_id,
    #     status=str(task_result.status),
    #     result=task_result.result,
    # )
