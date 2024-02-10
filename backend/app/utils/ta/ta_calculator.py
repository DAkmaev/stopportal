import datetime
import logging
import time
import concurrent.futures
from typing import List
from dataclasses import dataclass

import asyncio
import pandas as pd
from pandas import DataFrame
import pandas_ta as ta

from app.utils.moex.moex_reader import MoexReader
from app.utils.yahoo.yahoo_reader import YahooReader
from app.web.api.ta.scheme import TADecisionEnum, TADecisionDTO, TACompanyDTO
from app.web.api.company.scheme import CompanyTypeEnum
from app.db.models.company import StopModel, CompanyModel

pd.options.mode.chained_assignment = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TADecision:
    decision: TADecisionEnum
    df: DataFrame


class TACalculator:
    def generate_ta_indicators(self, df: DataFrame, period: str = "D"):
        if period == "W":
            # Функция для определения начала недели с понедельника
            def week_start(date):
                return date - pd.DateOffset(days=date.weekday())

            # Группируем данные по неделям, начиная с понедельника, и вычисляем необходимые агрегированные значения
            df = df.groupby(week_start)[["OPEN", "CLOSE", "HIGH", "LOW"]].agg(
                {"OPEN": "first", "CLOSE": "last", "HIGH": "max", "LOW": "min"}
            )

            # Удаляем последнюю строку, если она не является полной неделей
            # if df.index[-1] + pd.DateOffset(weeks=1) > last_row.name:
            #     df = df.iloc[:-1]

        elif period == "M":

            def month_start(date):
                return date.replace(day=1)

            # Группируем данные по месяцам и вычисляем необходимые агрегированные значения
            df = df.groupby(month_start)[["OPEN", "CLOSE", "HIGH", "LOW"]].agg(
                {"OPEN": "first", "CLOSE": "last", "HIGH": "max", "LOW": "min"}
            )

            # Удаляем последнюю строку, если она не является полным месяцем
            # if df.index[-1] == last_row.name.replace(day=1):
            #     df = df.iloc[:-1]

        # print(df)
        if len(df.index) <= 15:
            return DataFrame()

        # return df
        indicators = self._generate_ta_df(df)
        return indicators

    # Вынесено в отдельный метод для тестирования
    def _generate_ta_df(self, df: DataFrame):
        try:
            df.fillna(0, inplace=True)
            df.ta.adx(append=True)
            df.ta.stoch(append=True)

            df = df[
                ["STOCHk_14_3_3", "STOCHd_14_3_3", "ADX_14", "DMP_14", "DMN_14"]
            ].rename(
                columns={
                    "STOCHk_14_3_3": "k",
                    "STOCHd_14_3_3": "d",
                    "ADX_14": "adx",
                    "DMP_14": "dmp",
                    "DMN_14": "dmn",
                }
            )
            return df
        except Exception as e:
            logger.error(e)
            return DataFrame()

    def _get_period_decision(
        self,
        df: DataFrame,
        period: str,
        skip_check_borders: bool = False,
        bottom_border: float = 25,
        top_border: float = 80,
    ) -> TADecision:

        if df.empty:
            return TADecision(decision=TADecisionEnum.UNKNOWN, df=None)

        stoch_df = self.generate_ta_indicators(df, period)
        if stoch_df.empty:
            return TADecision(decision=TADecisionEnum.UNKNOWN, df=None)

        last_row = stoch_df.iloc[-1]
        need_buy = last_row.d < last_row.k and (
            skip_check_borders or last_row.k < bottom_border
        )
        need_sell = last_row.d > last_row.k and (
            skip_check_borders or last_row.k > top_border
        )

        decision = (
            TADecisionEnum.BUY
            if need_buy
            else TADecisionEnum.SELL
            if need_sell
            else TADecisionEnum.RELAX
        )
        return TADecision(decision=decision, df=stoch_df)

    def _calculate_decision(
        self, company: CompanyModel, period: str, df: DataFrame, last_price: float
    ):
        # Для некоторых акций увеличиваем bottom_border
        TIKERS_HIGH_BOTTOM = ["LKOH"]
        bottom_border = 40 if company.tiker in TIKERS_HIGH_BOTTOM else 25

        # для продажи проверяем границы и разворот для всех периодов
        per_decision = self._get_period_decision(
            df, period, bottom_border=bottom_border
        )

        if per_decision.decision == TADecisionEnum.UNKNOWN:
            return TADecisionDTO(
                decision=per_decision.decision,
                period=period,
                company=TACompanyDTO(
                    id=company.id, name=company.name, tiker=company.tiker
                ),
            )

        # для покупки проверяем другие периоды, они должны сопавсть, без границ
        # месяц считается полностью по _get_period_decision, это остальные по другому
        if period != "M" and per_decision.decision != TADecisionEnum.SELL:
            need_buy = False
            if period == "W":
                decision_month = self._get_period_decision(
                    df, "M", skip_check_borders=True
                )
                decision_week = self._get_period_decision(df, "W", bottom_border=40)

                need_buy = (
                    decision_month.decision
                    == decision_week.decision
                    == TADecisionEnum.BUY
                )

            elif period == "D":
                decision_day = self._get_period_decision(df, "D")
                decision_week = self._get_period_decision(df, "W", True)
                decision_month = self._get_period_decision(df, "M", True)

                need_buy = (
                    decision_day.decision
                    == decision_week.decision
                    == decision_month.decision
                    == TADecisionEnum.BUY
                )

            per_decision.decision = (
                TADecisionEnum.BUY if need_buy else TADecisionEnum.RELAX
            )

        last_row = per_decision.df.iloc[-1]
        return TADecisionDTO(
            company=TACompanyDTO(id=company.id, name=company.name, tiker=company.tiker),
            decision=per_decision.decision,
            period=period,
            k=last_row.k,
            d=last_row.d,
            last_price=last_price,
        )

    def get_history_data(
        self,
        company: CompanyModel,
        days_diff_month: int = 30 * 31,
        add_current: bool = True,
    ):
        start = (datetime.datetime.now() - datetime.timedelta(days_diff_month)).date()
        mreader = MoexReader()
        df = (
            mreader.get_company_history(
                start=start, tiker=company.tiker, add_current=add_current
            )
            if company.type == CompanyTypeEnum.MOEX
            else YahooReader.get_company_history(start=start, tiker=company.tiker)
        )

        return df

    def get_company_ta_decisions(
        self, company: CompanyModel, period: str
    ) -> dict[str, TADecisionDTO]:

        df = self.get_history_data(company)
        # df.dropna(inplace=True)
        results = dict()

        for cur_period in ["M", "W", "D"]:
            if period == cur_period or period == "ALL":

                # проверяем, что вообще есть данные
                if df.size == 0:
                    results[cur_period] = TADecisionDTO(
                        decision=TADecisionEnum.UNKNOWN,
                        period=cur_period,
                        company=TACompanyDTO(
                            id=company.id, name=company.name, tiker=company.tiker
                        ),
                    )
                    continue

                last_price = df.iloc[-1]["CLOSE"]
                stops_or_none = (
                    None
                    if not company.stops
                    else list(filter(lambda s: s.period == cur_period, company.stops))
                )
                stop = (
                    stops_or_none[0]
                    if stops_or_none and stops_or_none[0] is not None
                    else None
                )

                # Проверяем, что не пробит стоп
                if stops_or_none and last_price <= stop.value:
                    results[cur_period] = TADecisionDTO(
                        company=TACompanyDTO(
                            id=company.id, name=company.name, tiker=company.tiker
                        ),
                        period=cur_period,
                        decision=TADecisionEnum.SELL,
                        last_price=last_price,
                        stop=stop.value,
                    )
                else:
                    results[cur_period] = self._calculate_decision(
                        company, cur_period, df, last_price
                    )

        return results

    async def get_companies_ta_decisions(
        self, companies: list[CompanyModel], period: str
    ):
        decisions = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            tasks = [
                executor.submit(self.get_company_ta_decisions, company, period)
                for company in companies
            ]

            decisions = [task.result() for task in tasks]

        # for company in companies:
        #     print(f'get_company_ta_decisions {company.tiker}: ')
        #     decisions.append(self.get_company_ta_decisions(company, period))

        return decisions
