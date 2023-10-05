import asyncio
import logging
from _datetime import datetime
from typing import List

from fastapi import APIRouter, Depends

from backend.db.dao.cron_job import CronJobRunDao
from backend.db.dao.stock import StockDAO
from backend.utils.telegram.telegramm_client import send_tg_message
from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionModel

router = APIRouter()


@router.get("/")
async def get_stochs(
    period: str = 'W',
    is_cron: bool = False,
    stock_dao: StockDAO = Depends(),
    cron_dao: CronJobRunDao = Depends(),
    stoch_calculator: StochCalculator = Depends()
) -> List[StochDecisionModel]:

    if is_cron:
        CRON_JOB_NAME = 'CheckStoch'
        last_run = await cron_dao.get_cron_job_run_by_params(period, CRON_JOB_NAME)

        if last_run and last_run.last_run_date.date() == datetime.today().date():
            return []

        await cron_dao.update_cron_job_run(period, CRON_JOB_NAME)

    def fill_message(decision: str, stocks: List[StochDecisionModel],
                     period: str):
        if len(stocks) == 0:
            return ''

        period_str = 'месяц' if period == 'M' else 'день' if period == 'D' else 'неделя'

        result = f'Акции {decision} ({period_str})!\n'
        for dec in stocks:
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

    stocks = await stock_dao.get_all_stocks()

    des_futures = [
        stoch_calculator.get_stoch_decision(
            st.tiker,
            st.type,
            period,
            st.stops[0].value if st.stops else None
        ) for st in stocks]
    decisions = await asyncio.gather(*des_futures)

    stocks_to_buy = list(
        filter(lambda d: d.decision == StochDecisionEnum.BUY, decisions))
    stocks_to_sell = list(
        filter(lambda d: d.decision == StochDecisionEnum.SELL, decisions))
    stocks_to_relax = list(
        filter(lambda d: d.decision == StochDecisionEnum.RELAX, decisions))

    await asyncio.gather(
        send_tg_message(fill_message("продавать", stocks_to_sell, period)),
        send_tg_message(fill_message("покупать", stocks_to_buy, period)),
        send_tg_message(fill_message("тест", stocks_to_relax, period))
    )

    return decisions


@router.get("/{tiker}")
async def get_stoch(
    tiker: str,
    period: str = 'W',
    type: str = 'MOEX',
    stock_dao: StockDAO = Depends(),
    stoch_calculator: StochCalculator = Depends()
):
    stocks = await stock_dao.filter(tiker=tiker)
    stops_same_period = list(filter(lambda s: s.period == period, stocks[0].stops))
    stop_value = stops_same_period[0].value if stops_same_period else None

    decision_model = await stoch_calculator.get_stoch_decision(tiker, type, period, stop_value)

    message = f""" Акции {tiker}
    Вывод: {decision_model.decision.name}
    """

    await send_tg_message(message)

    return decision_model
