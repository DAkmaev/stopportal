from typing import List

from app.db.dao.companies import CompanyDAO
from app.db.dao.ta_decisions import TADecisionDAO
from app.schemas.ta import TADecisionDTO, TAMessageResponse, TAMessageStatus
from app.web.deps import CurrentUser
from app.worker import ta_final_task, ta_generate_task
from celery import group
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
        tiker,
        user_id,
        period,
        send_messages,
        update_db,
    )
    return TAMessageResponse(id=result.task_id, status=result.status)


@router.post("/")
async def generate_ta_decisions(  # noqa: WPS211
    current_user: CurrentUser,
    period: str = "All",
    send_messages: bool = True,
    update_db: bool = True,
    send_test_message: bool = False,
    company_dao: CompanyDAO = Depends(),
) -> TAMessageResponse:
    companies = await company_dao.get_all_companies(current_user.id)

    task_group = group(
        ta_generate_task.s(company.tiker, current_user.id, period)
        for company in companies
    )
    task_chain = task_group | ta_final_task.s(
        current_user.id,
        send_messages,
        update_db,
        send_test_message,
    )

    result = task_chain.apply_async()

    return TAMessageResponse(id=result.id, status=result.status)


@router.get("/task/{task_id}")
def get_task_status(task_id: str) -> TAMessageStatus:
    task_result = AsyncResult(task_id)
    return TAMessageStatus(
        id=task_id,
        status=task_result.status,
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
