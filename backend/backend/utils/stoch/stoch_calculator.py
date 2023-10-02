import datetime

import btalib
import pandas as pd
from pandas import DataFrame

from backend.utils.moex.moex_reader import MoexReader
from backend.utils.yahoo.yahoo_reader import YahooReader
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionModel
from backend.web.api.stock.scheme import StockTypeEnum


class StochCalculator:
    async def get_stoch(self,  df: DataFrame, period: str = "D"):

        if period == "W":
            # Функция для определения начала недели с понедельника
            def week_start(date):
                return date - pd.DateOffset(days=date.weekday())

            # Группируем данные по неделям, начиная с понедельника, и вычисляем необходимые агрегированные значения
            df = df.groupby(week_start)[
                ['OPEN', 'CLOSE', 'HIGH', 'LOW']].agg(
                {'OPEN': 'first', 'CLOSE': 'last', 'HIGH': 'max', 'LOW': 'min'})

        elif period == "M":
            def month_start(date):
                return date.replace(day=1)

            # Группируем данные по месяцам и вычисляем необходимые агрегированные значения
            df = df.groupby(month_start)[
                ['OPEN', 'CLOSE', 'HIGH', 'LOW']].agg(
                {'OPEN': 'first', 'CLOSE': 'last', 'HIGH': 'max', 'LOW': 'min'})

        #print(df)

        stoch = btalib.stochastic(df)
        #print(stoch.df)

        return stoch

    async def get_stoch_decision(self, tiker: str, type: str, period: str) -> StochDecisionModel:
        days_diff = 30 if period == 'D' else 30 * 7 if period == 'W' else 30 * 31
        start = (datetime.datetime.now() - datetime.timedelta(days_diff)).date()

        df = MoexReader.get_stock_history(start, tiker) if type == StockTypeEnum.MOEX else YahooReader.get_stock_history(start, tiker)

        stoch = await StochCalculator().get_stoch(df, period)

        last_row = stoch.df.iloc[-1]
        previous_row = stoch.df.iloc[-2]

        is_cross_lines_buy = last_row.k > last_row.d and previous_row.k < previous_row.d
        is_cross_lines_sell = last_row.k < last_row.d and previous_row.k > previous_row.d

        need_buy = is_cross_lines_buy and last_row.k < 25
        need_sell = is_cross_lines_sell and last_row.d > 80
        decision = StochDecisionEnum.BUY if need_buy else StochDecisionEnum.SELL if need_sell else StochDecisionEnum.RELAX

        return StochDecisionModel(
            decision=decision,
            k=last_row.k,
            d=last_row.d,
            k_previous=previous_row.k,
            d_previous=previous_row.d,
            tiker=tiker
        )


