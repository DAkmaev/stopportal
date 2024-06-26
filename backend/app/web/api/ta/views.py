from typing import List

from app.db.dao.ta_decisions import TADecisionDAO
from app.db.dependencies import get_sync_db_session
from app.schemas.ta import (
    TADecisionDTO,
    TAMessageResponse,
    TAMessageStatus,
    TAGenerateMessage,
)
from app.services.ta_bulk_service import TABulkService
from app.web.deps import CurrentUser
from app.worker import ta_generate_task
from celery.result import AsyncResult
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/{tiker}")
async def generate_ta_decision(
    tiker: str,
    current_user: CurrentUser,
    period: str = "All",
    send_messages: bool = True,
    update_db: bool = False,
) -> TAMessageResponse:
    user_id = current_user.id
    result = ta_generate_task.delay(
        TAGenerateMessage(
            tiker=tiker,
            user_id=user_id,
            period=period,
            send_message=send_messages,
            update_db=update_db,
        ).model_dump_json(),
    )
    return TAMessageResponse(id=result.task_id, status=result.status)


@router.post("/")
async def generate_ta_decisions(  # noqa: WPS211
    current_user: CurrentUser,
    period: str = "All",
    send_messages: bool = True,
    update_db: bool = True,
    send_test_message: bool = False,
) -> TAMessageResponse:
    with get_sync_db_session() as db:
        ta_bulk_service = TABulkService(db)
        return ta_bulk_service.generate_ta_decisions(
            user_id=current_user.id,
            period=period,
            send_messages=send_messages,
            update_db=update_db,
            send_test_message=send_test_message,
        )


@router.get("/task/{task_id}")
def get_task_status(task_id: str) -> TAMessageStatus:
    task_result = AsyncResult(task_id)
    return TAMessageStatus(
        id=task_id,
        status=str(task_result.status),
        result=task_result.result,
    )


@router.get("/")
async def get_ts_decisions(stoch_dao: TADecisionDAO = Depends()) -> List[TADecisionDTO]:
    return await stoch_dao.get_ta_decision_models()


# @router.get("/history/{tiker}")
# async def get_history_stochs(
#     tiker: str,
#     current_user: CurrentUser,
#     ta_service: TAService = Depends(),
# ):
#     result = await ta_service.history_stochs(tiker, current_user.id)
#     return FileResponse(
#         os.path.join(result["path"], result["file_name"]),
#         media_type="application/octet-stream",
#         filename=result["file_name"],
#     )
