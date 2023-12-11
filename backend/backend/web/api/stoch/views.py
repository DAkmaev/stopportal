import asyncio
import logging
import time
from _datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Depends

from backend.db.dao.cron_job import CronJobRunDao
from backend.db.dao.companies import CompanyDAO
from backend.db.dao.stoch_decisions import StochDecisionDAO
from backend.utils.telegram.telegramm_client import send_tg_message
from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionDTO
from backend.services.stoch_service import StochService

router = APIRouter()
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/")
async def generate_stoch_decisions(
    period: str = 'ALL',
    is_cron: bool = False,
    send_messages: bool = True,
    send_test: bool = False,
    stoch_service: StochService = Depends()
) -> Dict[str, Dict[str, List[StochDecisionDTO]]]:
    stochs = await stoch_service.generate_stoch_decisions(period, is_cron, send_messages, send_test)
    return stochs


@router.post("/{tiker}")
async def generate_stoch_decision(
    tiker: str,
    period: str = 'W',
    type: str = 'MOEX',
    send_messages: bool = False,
    company_dao: CompanyDAO = Depends(),
    stoch_calculator: StochCalculator = Depends(),
    stoch_service: StochService = Depends()
) -> Dict[str, StochDecisionDTO]:
    return await stoch_service.generate_stoch_decision(
        tiker=tiker, period=period,send_messages=send_messages
    )

@router.get("/")
async def get_stochs(
    stoch_dao: StochDecisionDAO = Depends()
) -> List[StochDecisionDTO]:
    stochs = await stoch_dao.get_stoch_decision_models()
    return stochs
