from typing import Dict, List

from app.db.dao.user import UserDAO
from app.services.ta_service import TAService
from app.web.api.ta.scheme import TADecisionDTO
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/ta/{user_id}")
async def cron_generate_ta_decisions(  # noqa: WPS211
    user_id: int,
    period: str = "ALL",
    send_messages: bool = True,
    send_test: bool = False,
    ta_service: TAService = Depends(),
    user_dao: UserDAO = Depends(),
) -> Dict[str, Dict[str, List[TADecisionDTO]]]:
    user = await user_dao.get_user(user_id=user_id)

    return await ta_service.generate_ta_decisions(
        user=user,
        period=period,
        send_messages=send_messages,
        send_test=send_test,
    )
