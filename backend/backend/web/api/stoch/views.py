import asyncio
from typing import List, Dict, Any

from fastapi import APIRouter, Depends

from backend.db.dao.stock import StockDAO
from backend.services.StochService import StochService
from backend.utils.stoch import stoch_calculator
from backend.utils.telegram.telegramm_client import send_tg_message
from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionModel

router = APIRouter()


@router.get("/")
async def get_stochs(
    period: str = 'W',
    stock_dao: StockDAO = Depends(),
    stoch_calculator: StochCalculator = Depends()
) -> List[StochDecisionModel]:
    def fill_message(decision: str, stocks: List[StochDecisionModel],
                     period: str):
        if len(stocks) == 0:
            return ''

        period_str = 'месяц' if period == 'M' else 'день' if period == 'D' else 'неделя'

        result = f'Акции {decision} ({period_str})!\n'
        for dec in stocks:
            k = round(dec.k, 2)
            k_prev = round(dec.k_previous, 2)
            d = round(dec.d, 2)
            d_prev = round(dec.d_previous, 2)
            name = f'[{dec.tiker}](https://www.moex.com/ru/issue.aspx?board=TQBR&code={dec.tiker})'
            result += f'{name} - k: {k}, d: {d}, k prev: {k_prev}, d prev: {d_prev}\n'
        return result

    stocks = await stock_dao.get_all_stocks()

    des_futures = [
        stoch_calculator.get_stoch_decision(st.tiker, st.type, period) for st
        in stocks]
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
    stoch_calculator: StochCalculator = Depends()
):
    decision_model = await stoch_calculator.get_stoch_decision(tiker, type, period)

    message = f""" Акции {tiker}
    Вывод: {decision_model.decision.name}
    """

    await send_tg_message(message)

    return decision_model
