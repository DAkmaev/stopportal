from typing import List
import asyncio

from backend.db.dao.stock import StockDAO
from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.web.api.stoch.scheme import StochDecisionModel, StochDecisionEnum


class StochService:
    def init(self):
        self.stock_dao = StockDAO()
        self.stoch_calculator = StochCalculator()

    def fill_message(self, decision: str, stocks: List[StochDecisionModel],
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

    async def get_stochs(self, period: str = 'W'):
        stocks = await self.stock_dao.get_all_stocks()

        des_futures = [
            self.stoch_calculator.get_stoch_decision(st.tiker, st.type, period) for st
            in stocks]
        decisions = await asyncio.gather(*des_futures)

        stocks_to_buy = list(
            filter(lambda d: d.decision == StochDecisionEnum.BUY, decisions))
        stocks_to_sell = list(
            filter(lambda d: d.decision == StochDecisionEnum.SELL, decisions))
        stocks_to_relax = list(
            filter(lambda d: d.decision == StochDecisionEnum.RELAX, decisions))

        return {
            "stocks_to_buy": stocks_to_buy,
            "stocks_to_sell": stocks_to_sell,
            "stocks_to_relax": stocks_to_relax
        }
