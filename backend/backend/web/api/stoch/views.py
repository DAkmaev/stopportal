import asyncio
import logging
import time
from _datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Depends

from backend.db.dao.cron_job import CronJobRunDao
from backend.db.dao.companies import CompanyDAO
from backend.utils.telegram.telegramm_client import send_tg_message
from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionModel
from backend.services.stoch_service import StochService

router = APIRouter()
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/")
async def get_stochs(
    period: str = 'ALL',
    is_cron: bool = False,
    send_messages: bool = True,
    send_test: bool = False,
    stoch_service: StochService = Depends()
) -> Dict[str, Dict[str, List[StochDecisionModel]]]:
    stochs = await stoch_service.get_stochs(period, is_cron, send_messages, send_test)
    return stochs


@router.get("/{tiker}")
async def get_stoch(
    tiker: str,
    period: str = 'W',
    type: str = 'MOEX',
    send_messages: bool = False,
    company_dao: CompanyDAO = Depends(),
    stoch_calculator: StochCalculator = Depends(),
    stoch_service: StochService = Depends()
) -> Dict[str, StochDecisionModel]:
    return await stoch_service.get_stoch(
        tiker=tiker, period=period,send_messages=send_messages
    )
