from typing import List

from server.src.db.dao.ta_decisions import TADecisionDAO
from server.src.schemas.ta import TADecisionDTO
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/")
async def get_ts_decisions(stoch_dao: TADecisionDAO = Depends()) -> List[TADecisionDTO]:
    return await stoch_dao.get_ta_decision_models()



