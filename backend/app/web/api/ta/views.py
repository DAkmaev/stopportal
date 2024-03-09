import os
from typing import Dict, List

from app.db.dao.ta_decisions import TADecisionDAO
from app.services.ta_service import TAService
from app.web.api.ta.scheme import TADecisionDTO
from app.web.deps import CurrentUser
from fastapi import APIRouter, Depends
from starlette.responses import FileResponse

router = APIRouter()


@router.post("/")
async def generate_ta_decisions(  # noqa: WPS211
    current_user: CurrentUser,
    period: str = "ALL",
    send_messages: bool = True,
    send_test: bool = False,
    ta_service: TAService = Depends(),
) -> Dict[str, Dict[str, List[TADecisionDTO]]]:
    return await ta_service.generate_ta_decisions(
        user=current_user,
        period=period,
        send_messages=send_messages,
        send_test=send_test,
    )


@router.post("/{tiker}")
async def generate_ta_decision(
    tiker: str,
    current_user: CurrentUser,
    period: str = "W",
    send_messages: bool = False,
    ta_service: TAService = Depends(),
) -> Dict[str, TADecisionDTO]:
    return await ta_service.generate_ta_decision(
        tiker=tiker,
        period=period,
        send_messages=send_messages,
        user_id=current_user.id,
    )


@router.get("/")
async def get_stochs(stoch_dao: TADecisionDAO = Depends()) -> List[TADecisionDTO]:
    return await stoch_dao.get_ta_decision_models()


@router.get("/history/{tiker}")
async def get_history_stochs(
    tiker: str,
    current_user: CurrentUser,
    ta_service: TAService = Depends(),
):
    result = await ta_service.history_stochs(tiker, current_user.id)
    return FileResponse(
        os.path.join(result["path"], result["file_name"]),
        media_type="application/octet-stream",
        filename=result["file_name"],
    )
