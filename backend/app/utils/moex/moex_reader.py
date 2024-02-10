import datetime
from typing import Optional, Tuple

import apimoex
import pandas as pd
import requests
from pandas import DataFrame


class MoexReader:
    def get_company_history(  # noqa: WPS210
        self, start: datetime, tiker: str, add_current: bool = True,
    ) -> DataFrame:

        columns = ("OPEN", "HIGH", "LOW", "TRADEDATE", "CLOSE", "VOLUME", "VALUE")
        candle_start = datetime.datetime.today().strftime("%Y-%m-%d")

        with requests.Session() as session:
            data = self._fetch_board_history(session, tiker, start, columns)
            if add_current:
                candles = self._fetch_board_candles(session, tiker, candle_start)

            if add_current and data and candles:
                last_candle = candles[-1]
                last_data = {
                    "OPEN": last_candle.get("open"),
                    "CLOSE": last_candle.get("close"),
                    "LOW": last_candle.get("low"),
                    "HIGH": last_candle.get("high"),
                    "VALUE": last_candle.get("value"),
                    "VOLUME": last_candle.get("volume"),
                    "TRADEDATE": candle_start,
                }

                if candle_start == data[-1]["TRADEDATE"]:
                    data[-1] = last_data
                else:
                    data.append(last_data)

            df = DataFrame(data)
            if df.size > 0:
                df["TRADEDATE"] = pd.to_datetime(df["TRADEDATE"])
                df.set_index("TRADEDATE", inplace=True)
            return df

    def _fetch_board_history(
        self,
        session: requests.Session(),
        tiker: str,
        start: datetime,
        columns: Optional[Tuple[str, ...]],
    ) -> dict:

        return apimoex.get_board_history(
            session, security=tiker, start=str(start), columns=columns,
        )

    def _fetch_board_candles(
        self, session: requests.Session(), tiker: str, start: datetime,
    ) -> list:

        return apimoex.get_board_candles(
            session, security=tiker, interval=10, start=str(start), columns=None,
        )
