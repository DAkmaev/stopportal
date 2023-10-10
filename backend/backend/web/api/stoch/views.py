import asyncio
import logging
from _datetime import datetime
from typing import List

from fastapi import APIRouter, Depends

from backend.db.dao.cron_job import CronJobRunDao
from backend.db.dao.companies import CompanyDAO
from backend.utils.telegram.telegramm_client import send_tg_message
from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionModel

router = APIRouter()


@router.get("/")
async def get_stochs(
    period: str = 'W',
    is_cron: bool = False,
    send_messages: bool = True,
    send_test: bool = False,
    company_dao: CompanyDAO = Depends(),
    cron_dao: CronJobRunDao = Depends(),
    stoch_calculator: StochCalculator = Depends()
) -> List[StochDecisionModel]:

    if is_cron:
        CRON_JOB_NAME = 'CheckStoch'
        last_run = await cron_dao.get_cron_job_run_by_params(period, CRON_JOB_NAME)

        if last_run and last_run.last_run_date.date() == datetime.today().date():
            return []

        await cron_dao.update_cron_job_run(period, CRON_JOB_NAME)

    def fill_message(decision: str, companies: List[StochDecisionModel],
                     period: str):
        if len(companies) == 0:
            return ''

        period_str = 'месяц' if period == 'M' else 'день' if period == 'D' else 'неделя'

        result = f'Акции {decision} ({period_str})!\n'
        for dec in companies:
            name = f'[{dec.tiker}](https://www.moex.com/ru/issue.aspx?board=TQBR&code={dec.tiker})'
            price_str = f' - цена: {round(dec.last_price, 2)}'
            stop_str = f', стоп: {round(dec.stop, 2)}' if dec.stop else ''
            stoch_data_str = ''
            if dec.k and dec.d:
                k = round(dec.k, 2)
                d = round(dec.d, 2)
                stoch_data_str = f', k: {k}, d: {d}'

            result += f'{name}{price_str}{stop_str}{stoch_data_str}\n'

        return result

    companies = await company_dao.get_all_companies()

    des_futures = [
        stoch_calculator.get_stoch_decision(
            st.tiker,
            st.type,
            period,
            st.stops[0].value if st.stops else None
        ) for st in companies]
    decisions = await asyncio.gather(*des_futures)

    companies_to_buy = list(
        filter(lambda d: d.decision == StochDecisionEnum.BUY, decisions))
    companies_to_sell = list(
        filter(lambda d: d.decision == StochDecisionEnum.SELL, decisions))
    companies_to_relax = list(
        filter(lambda d: d.decision == StochDecisionEnum.RELAX, decisions))

    if send_messages:
        send_tasks = [
            send_tg_message(fill_message("продавать", companies_to_sell, period)),
            send_tg_message(fill_message("покупать", companies_to_buy, period))
        ]
        if send_test:
            send_tasks.append(send_tg_message(fill_message("тест", companies_to_relax, period)))

        await asyncio.gather(*send_tasks)

    return decisions


@router.get("/{tiker}")
async def get_stoch(
    tiker: str,
    period: str = 'W',
    type: str = 'MOEX',
    company_dao: CompanyDAO = Depends(),
    stoch_calculator: StochCalculator = Depends()
):
    companies = await company_dao.filter(tiker=tiker)
    stops_same_period = list(filter(lambda s: s.period == period, companies[0].stops))
    stop_value = stops_same_period[0].value if stops_same_period else None

    decision_model = await stoch_calculator.get_stoch_decision(tiker, type, period, stop_value)

    message = f""" Акции {tiker}
    Вывод: {decision_model.decision.name}
    """

    await send_tg_message(message)

    return decision_model
