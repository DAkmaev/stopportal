import logging

from server.src.schemas.ta import TAStartGenerateMessage, TAPeriodEnum
from fastapi import APIRouter, Depends

from server.src.worker import app as celery_app
from server.src.auth import CurrentUser

router = APIRouter()


# @router.get("/")
# async def get_ts_decisions(stoch_dao: TADecisionDAO = Depends()) -> List[TADecisionDTO]:
#     return await stoch_dao.get_ta_decision_models()


@router.post("/")
async def run_generate_ts_decisions(
        current_user: CurrentUser,
):
    message = TAStartGenerateMessage(
        user_id=current_user.id,
        period=TAPeriodEnum.DAY,
        companies=[]
    )
    payload_str = str(message.model_dump_json())
    result = celery_app.send_task('worker.src.tasks.start_generate_task', args=[payload_str]) #, queue='run_calculation')
    logging.info(f"Result: {str(result)}")
