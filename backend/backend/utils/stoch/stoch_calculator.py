import datetime
from dataclasses import dataclass

import btalib
import pandas as pd
from pandas import DataFrame

from backend.utils.moex.moex_reader import MoexReader
from backend.utils.yahoo.yahoo_reader import YahooReader
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionModel
from backend.web.api.company.scheme import CompanyTypeEnum


@dataclass
class StochDecision:
    decision: StochDecisionEnum
    df: DataFrame


class StochCalculator:
    async def _get_stoch(self,  df: DataFrame, period: str = "D"):

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

    async def get_period_decision(
        self,  df: DataFrame, period: str, skip_check_borders: bool = False
    ) -> StochDecision:

        stoch = await StochCalculator()._get_stoch(df, period)
        last_row = stoch.df.iloc[-1]
        need_buy = last_row.d < last_row.k and (skip_check_borders or last_row.k < 25)
        need_sell = last_row.d > last_row.k and (skip_check_borders or last_row.k > 80)

        decision = (
            StochDecisionEnum.BUY if need_buy
            else StochDecisionEnum.SELL if need_sell
            else StochDecisionEnum.RELAX
        )

        return StochDecision(decision=decision, df=stoch.df)

    async def get_stoch_decision(self, tiker: str, type: str, period: str, stop: float | None) -> StochDecisionModel:
        # days_diff_day = 30
        # days_diff_week = days_diff_day * 7
        # исторические данные за период, которого хватит для сточ помесячно (ну и день/неделя тоже)
        days_diff_month = 30 * 31

        start = (datetime.datetime.now() - datetime.timedelta(days_diff_month)).date()
        df = (MoexReader.get_company_history(start, tiker) if type == CompanyTypeEnum.MOEX else YahooReader.get_company_history(start, tiker))

        if df.size == 0:
            return StochDecisionModel(
                decision=StochDecisionEnum.UNKNOWN,
                tiker=tiker
            )

        last_price = df.iloc[-1]['CLOSE']
        if stop and last_price <= stop:
            return StochDecisionModel(
                decision=StochDecisionEnum.SELL,
                last_price=last_price,
                stop=stop,
                tiker=tiker
            )

        # для продажи проверяем границы и разворот
        per_decision = await self.get_period_decision(df, period)
        # для покупки проверяем другие периоды, они должны сопавсть, без границ
        if per_decision.decision != StochDecisionEnum.SELL and period != 'M':
            decision_week = await self.get_period_decision(df, 'W', True)
            decision_month = await self.get_period_decision(df, 'M', True)
            need_buy = (decision_month.decision == decision_week.decision and
                        decision_week.decision == StochDecisionEnum.BUY)

            if period == 'D':
                decision_day = await self.get_period_decision(df, 'D', True)
                need_buy = need_buy and decision_day.decision == StochDecisionEnum.BUY

            per_decision.decision = StochDecisionEnum.BUY if need_buy else StochDecisionEnum.RELAX

        last_row = per_decision.df.iloc[-1]
        return StochDecisionModel(
            decision=per_decision.decision,
            k=last_row.k,
            d=last_row.d,
            last_price=last_price,
            tiker=tiker
        )


