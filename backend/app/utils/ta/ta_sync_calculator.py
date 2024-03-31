import datetime
import logging
import math
from dataclasses import dataclass

import pandas as pd
import pandas_ta as ta  # noqa: F401
from app.db.models.company import CompanyModel
from pandas import DataFrame

from app.schemas.Company import CompanyTypeEnum
from app.schemas.Ta import TADecisionDTO, TADecisionEnum, TACompanyDTO
from app.utils.moex.moex_reader import MoexReader
from app.utils.yahoo.yahoo_reader import YahooReader

pd.options.mode.chained_assignment = None

logger = logging.getLogger(__name__)


@dataclass
class TADecision:
    decision: TADecisionEnum
    df: DataFrame


class TACalculator:
    def generate_ta_indicators(self, df: DataFrame, period: str = "D"):
        if period == "W":
            # Функция для определения начала недели с понедельника
            def week_start(date):  # noqa: WPS430
                return date - pd.DateOffset(days=date.weekday())

            # Группируем данные по неделям, начиная с понедельника, и вычисляем
            # необходимые агрегированные значения
            df = df.groupby(week_start)[["OPEN", "CLOSE", "HIGH", "LOW"]].agg(
                {"OPEN": "first", "CLOSE": "last", "HIGH": "max", "LOW": "min"},
            )

            # Удаляем последнюю строку, если она не является полной неделей
            # if df.index[-1] + pd.DateOffset(weeks=1) > last_row.name:
            #     df = df.iloc[:-1]

        elif period == "M":

            def month_start(date):  # noqa: WPS430
                return date.replace(day=1)

            # Группируем данные по месяцам и вычисляем необходимые агрегированные
            # значения
            df = df.groupby(month_start)[["OPEN", "CLOSE", "HIGH", "LOW"]].agg(
                {"OPEN": "first", "CLOSE": "last", "HIGH": "max", "LOW": "min"},
            )

            # Удаляем последнюю строку, если она не является полным месяцем
            # if df.index[-1] == last_row.name.replace(day=1):
            #     df = df.iloc[:-1]

        # print(df)
        if len(df.index) <= 15:
            return DataFrame()

        # return df
        return self._generate_ta_df(df)

    def get_history_data(
        self,
        company: CompanyModel,
        days_diff_month: int = 30 * 31,
        add_current: bool = True,
    ):
        start = (datetime.datetime.now() - datetime.timedelta(days_diff_month)).date()
        mreader = MoexReader()
        return (
            mreader.get_company_history(
                start=start,
                tiker=company.tiker,
                add_current=add_current,
            )
            if company.type == CompanyTypeEnum.MOEX
            else YahooReader.get_company_history(start=start, tiker=company.tiker)
        )

    def get_company_ta_decisions(
        self,
        company: CompanyModel,
        period: str,
    ) -> dict[str, TADecisionDTO]:
        df = self.get_history_data(company)
        results = {}

        for cur_period in ("M", "W", "D"):
            if period in {cur_period, "All"}:
                logger.debug(
                    f"Start getting period decisions for {company.name}, {cur_period}",
                )
                results[cur_period] = self._process_period(df, cur_period, company)
                decision_name = results[cur_period].decision.name
                logger.debug(
                    f"Got period decisions for {cur_period}, {decision_name}",
                )
        results_count = len(results)
        logger.debug(f"Return company_ta_decisions results count {results_count}")
        return results

    # Вынесено в отдельный метод для тестирования
    def _generate_ta_df(self, df: DataFrame):
        try:
            df.fillna(0, inplace=True)
            df.ta.adx(append=True)
            df.ta.stoch(append=True)
            df.ta.macd(append=True)

            return df[
                [
                    "STOCHk_14_3_3",
                    "STOCHd_14_3_3",
                    "ADX_14",
                    "DMP_14",
                    "DMN_14",
                    "MACD_12_26_9",
                    "MACDh_12_26_9",
                    "MACDs_12_26_9",
                ]
            ].rename(
                columns={
                    "STOCHk_14_3_3": "k",
                    "STOCHd_14_3_3": "d",
                    "ADX_14": "adx",
                    "DMP_14": "dmp",
                    "DMN_14": "dmn",
                    "MACD_12_26_9": "macd",
                    "MACDh_12_26_9": "macd_h",
                    "MACDs_12_26_9": "macd_s",
                },
            )
        except Exception as ex:
            logger.error(ex)
            return DataFrame()

    def _get_period_decision(  # noqa: WPS211
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

        if need_buy:
            decision = TADecisionEnum.BUY
        elif need_sell:
            decision = TADecisionEnum.SELL
        else:
            decision = TADecisionEnum.RELAX

        return TADecision(decision=decision, df=stoch_df)

    def _calculate_decision(
        self,
        company: CompanyModel,
        period: str,
        df: DataFrame,
        last_price: float | None,
    ):
        # Determine bottom_border based on company.tiker
        bottom_border = 40 if company.tiker == "LKOH" else 25

        # Calculate decision for the given period
        per_decision = self._get_period_decision(
            df,
            period,
            bottom_border=bottom_border,
        )

        # Handle UNKNOWN decision
        if per_decision.decision == TADecisionEnum.UNKNOWN:
            return TADecisionDTO(
                decision=per_decision.decision,
                period=period,
                company=TACompanyDTO(
                    id=company.id,
                    name=company.name,
                    tiker=company.tiker,
                ),
            )

        # Calculate decision for buying
        if period != "M" and per_decision.decision != TADecisionEnum.SELL:
            need_buy = self._check_buy_decision(df, period)
            per_decision.decision = (
                TADecisionEnum.BUY if need_buy else TADecisionEnum.RELAX
            )

        # Prepare TADecisionDTO
        last_row = per_decision.df.iloc[-1]
        return TADecisionDTO(
            company=TACompanyDTO(id=company.id, name=company.name, tiker=company.tiker),
            decision=per_decision.decision,
            period=period,
            k=None if math.isnan(last_row.k) else last_row.k,
            d=None if math.isnan(last_row.d) else last_row.d,
            last_price=last_price,
        )

    def _check_buy_decision(self, df: DataFrame, period: str) -> bool:
        if period == "W":
            decision_month = self._get_period_decision(df, "M", skip_check_borders=True)
            decision_week = self._get_period_decision(df, "W", bottom_border=40)
            return (
                decision_month.decision == decision_week.decision == TADecisionEnum.BUY
            )

        elif period == "D":
            decision_day = self._get_period_decision(df, "D")
            decision_week = self._get_period_decision(df, "W", skip_check_borders=True)
            decision_month = self._get_period_decision(df, "M", skip_check_borders=True)
            return (
                decision_day.decision
                == decision_week.decision
                == decision_month.decision
                == TADecisionEnum.BUY
            )

        return False

    def _process_period(
        self,
        df: DataFrame,
        cur_period: str,
        company: CompanyModel,
    ) -> TADecisionDTO:
        if df.size == 0:
            return TADecisionDTO(
                decision=TADecisionEnum.UNKNOWN,
                period=cur_period,
                company=TACompanyDTO(
                    id=company.id,
                    name=company.name,
                    tiker=company.tiker,
                ),
            )

        last_price_value = df.iloc[-1]["CLOSE"]
        last_price = None if math.isnan(last_price_value) else last_price_value

        if last_price:
            stops_or_none = company.stops or []
            stop = next(
                (stop.value for stop in stops_or_none if stop.period == cur_period),
                None,
            )

            if stop is not None and last_price <= stop:
                return TADecisionDTO(
                    company=TACompanyDTO(
                        id=company.id,
                        name=company.name,
                        tiker=company.tiker,
                    ),
                    period=cur_period,
                    decision=TADecisionEnum.SELL,
                    last_price=last_price,
                    stop=stop,
                )
        return self._calculate_decision(company, cur_period, df, last_price)
