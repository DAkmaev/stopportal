import asyncio
import logging
from typing import List

from fastapi import APIRouter, Depends

from backend.app.db.dao.companies import CompanyDAO
from backend.app.db.dao.ta_decisions import TADecisionDAO
from backend.app.schemas.ta import TAMessageResponse, DecisionDTO
from backend.app.services.ta_service import TAService
from backend.app.worker.tasks import start_generate_task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ta/{user_id}/generate")
async def internal_start_generate_ta_decisions(  # noqa: WPS211
    user_id: int,
    period: str = "All",
    send_messages: bool = True,
    update_db: bool = True,
    send_test_message: bool = False,
    ta_service: TAService = Depends(),
) -> TAMessageResponse:
    message = await ta_service.fill_send_start_generate_message(
        user_id=user_id,
        period=period,
        send_messages=send_messages,
        update_db=update_db,
        send_test_message=send_test_message,
    )

    payload_str = str(message.model_dump_json())
    result = start_generate_task.delay(payload_str)
    logging.debug(f"********* payload: {result}")

    return TAMessageResponse(id=result.id, status=result.status)


@router.post("/ta/{user_id}")
async def internal_update_db_decisions(
    user_id: int,
    decisions: List[DecisionDTO],
    decisions_dao: TADecisionDAO = Depends(),
    company_dao: CompanyDAO = Depends(),
):
    tasks = []
    for decision in decisions:
        company = await company_dao.get_company_model_by_tiker(
            tiker=decision.tiker, user_id=user_id
        )
        task = decisions_dao.update_or_create_ta_decision_model(
            company=company,
            period=decision.period,
            decision=decision.decision,
            k=decision.k,
            d=decision.d,
            last_price=decision.last_price,
        )
        tasks.append(task)

    await asyncio.gather(*tasks)
