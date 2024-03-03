import os
from typing import Dict, List

from app.db.dao.ta_decisions import TADecisionDAO
from app.services.ta_service import TAService
from app.web.api.ta.scheme import TADecisionDTO
from fastapi import APIRouter, Depends
from starlette.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/")
async def generate_ta_decisions(
    period: str = "ALL",
    is_cron: bool = False,
    send_messages: bool = True,
    send_test: bool = False,
    ta_service: TAService = Depends(),
) -> Dict[str, Dict[str, List[TADecisionDTO]]]:
    # todo заменить на получение портфеля для user
    briefcase_id = 1

    return await ta_service.generate_ta_decisions(
        briefcase_id,
        period,
        is_cron,
        send_messages,
        send_test,
    )


@router.post("/{tiker}")
async def generate_ta_decision(
    tiker: str,
    period: str = "W",
    send_messages: bool = False,
    ta_service: TAService = Depends(),
) -> Dict[str, TADecisionDTO]:
    return await ta_service.generate_ta_decision(
        tiker=tiker,
        period=period,
        send_messages=send_messages,
    )


@router.get("/")
async def get_stochs(stoch_dao: TADecisionDAO = Depends()) -> JSONResponse:
    ta_data = await stoch_dao.get_ta_decision_models()
    return JSONResponse(content=jsonable_encoder(ta_data))


@router.get("/history/{tiker}")
async def get_history_stochs(
    tiker: str,
    ta_service: TAService = Depends(),
):
    result = await ta_service.history_stochs(tiker)
    return FileResponse(
        os.path.join(result["path"], result["file_name"]),
        media_type="application/octet-stream",
        filename=result["file_name"],
    )
