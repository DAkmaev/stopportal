import datetime
from typing import List
from dataclasses import dataclass

import btalib
import asyncio
import pandas as pd
from pandas import DataFrame

from backend.utils.moex.moex_reader import MoexReader
from backend.utils.yahoo.yahoo_reader import YahooReader
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionDTO, StochCompanyDTO
from backend.web.api.company.scheme import CompanyTypeEnum
from backend.db.models.company import StopModel, CompanyModel


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
        if len(df.index) < 15:
            return None

        stoch = btalib.stochastic(df)
        #print(stoch.df)

        return stoch

    async def _get_period_decision(
        self,  df: DataFrame, period: str,
        skip_check_borders: bool = False,
        bottom_border: float = 25,
        top_border: float = 80,
    ) -> StochDecision:

        if df.empty:
            return  StochDecision(decision=StochDecisionEnum.UNKNOWN, df=None)

        stoch = await StochCalculator()._get_stoch(df, period)
        if not stoch:
            return StochDecision(decision=StochDecisionEnum.UNKNOWN, df=None)

        last_row = stoch.df.iloc[-1]
        need_buy = last_row.d < last_row.k and (skip_check_borders or last_row.k < bottom_border)
        need_sell = last_row.d > last_row.k and (skip_check_borders or last_row.k > top_border)

        decision = (
            StochDecisionEnum.BUY if need_buy
            else StochDecisionEnum.SELL if need_sell
            else StochDecisionEnum.RELAX
        )
        return StochDecision(decision=decision, df=stoch.df)


    async def _calculate_decision(self, company: CompanyModel, period: str, df: DataFrame, stop: StopModel | None, last_price: float):
        # для продажи проверяем границы и разворот для всех периодов
        per_decision = await self._get_period_decision(df, period)

        if per_decision.decision == StochDecisionEnum.UNKNOWN:
            return StochDecisionDTO(
                decision=per_decision.decision,
                company=StochCompanyDTO(
                    id=company.id,
                    name=company.name,
                    tiker=company.tiker
                ))

        # для покупки проверяем другие периоды, они должны сопавсть, без границ
        # месяц считается полностью по _get_period_decision, это остальные по другому
        if period != 'M' and per_decision.decision != StochDecisionEnum.SELL:
            need_buy = False
            if period == 'W':
                decision_month, decision_week = await asyncio.gather(
                    self._get_period_decision(df, 'M', skip_check_borders=True),
                    self._get_period_decision(df, 'W', bottom_border=40)
                )
                need_buy = decision_month.decision == decision_week.decision == StochDecisionEnum.BUY

            elif period == 'D':
                decision_day, decision_week, decision_month = await asyncio.gather(
                    self._get_period_decision(df, 'D'),
                    self._get_period_decision(df, 'W', True),
                    self._get_period_decision(df, 'M', True)
                )

                need_buy = decision_day.decision == decision_week.decision == decision_month.decision == StochDecisionEnum.BUY

            per_decision.decision = StochDecisionEnum.BUY if need_buy else StochDecisionEnum.RELAX


        last_row = per_decision.df.iloc[-1]
        return StochDecisionDTO(
            company=StochCompanyDTO(
                id=company.id,
                name=company.name,
                tiker=company.tiker
            ),
            decision=per_decision.decision,
            period=period,
            k=last_row.k,
            d=last_row.d,
            last_price=last_price
        )



    async def get_stoch_decisions(
            self, company: CompanyModel, period: str
        ) -> dict[str, StochDecisionDTO]:
        days_diff_month = 30 * 31

        start = (datetime.datetime.now() - datetime.timedelta(days_diff_month)).date()
        mreader = MoexReader()
        df = (await mreader.get_company_history_async(start=start, tiker=company.tiker) if company.type == CompanyTypeEnum.MOEX else YahooReader.get_company_history(start=start, tiker=company.tiker))

        results = dict()

        for cur_period in ['M', 'W', 'D']:
            if period == cur_period or period == 'ALL':

                # проверяем, что вообще есть данные
                if df.size == 0:
                    results[cur_period] = StochDecisionDTO(
                        decision=StochDecisionEnum.UNKNOWN,
                        period=cur_period,
                        company=StochCompanyDTO(
                            id=company.id,
                            name=company.name,
                            tiker=company.tiker
                        )
                    )
                    continue

                last_price = df.iloc[-1]['CLOSE']
                stops_or_none = None if not company.stops else list(filter(lambda s: s.period == cur_period, company.stops))
                stop = stops_or_none[0] if stops_or_none and stops_or_none[0] is not None else None

                # Проверяем, что не пробит стоп
                if stops_or_none and last_price <= stop.value:
                    results[cur_period] = StochDecisionDTO(
                        company=StochCompanyDTO(
                            id=company.id,
                            name=company.name,
                            tiker=company.tiker
                        ),
                        period=cur_period,
                        decision=StochDecisionEnum.SELL,
                        last_price=last_price,
                        stop=stop.value
                    )
                else:
                    results[cur_period] = await self._calculate_decision(
                        company, cur_period, df, stop, last_price
                    )

        return results

