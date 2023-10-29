import asyncio
import datetime
import concurrent
from typing import Optional, Tuple

import apimoex
import pandas as pd
import requests
from pandas import DataFrame
from aiohttp import ClientSession


class MoexReader:
    def _fetch_board_history(
        self, session: requests.Session(), tiker: str,
        start: datetime, columns: Optional[Tuple[str, ...]]
    ) -> dict:

        return apimoex.get_board_history(
            session, security=tiker, start=str(start), columns=columns)

    def _fetch_board_candles(
        self, session: requests.Session(), tiker: str, start: datetime
    ) -> list:

        return apimoex.get_board_candles(
            session, security=tiker, interval=10, start=str(start), columns=None)

    async def get_company_history_async(
            self, start: datetime, tiker: str, add_current: bool = True) -> DataFrame:

        COLUMNS = ("OPEN", "HIGH", "LOW", "TRADEDATE", "CLOSE", "VOLUME", "VALUE")
        candle_start = datetime.datetime.today().strftime('%Y-%m-%d')

        with requests.Session() as session:

            with concurrent.futures.ThreadPoolExecutor() as executor:
                data = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: self._fetch_board_history(session, tiker, start, COLUMNS)
                )
                if add_current:
                    candles = await asyncio.get_event_loop().run_in_executor(
                        executor,
                        lambda: self._fetch_board_candles(session, tiker, candle_start)
                    )
            #
            # tasks = [
            #     self._fetch_board_history(
            #         session, tiker=tiker,start=start, columns=COLUMNS),
            # ]
            # if add_current:
            #     with concurrent.futures.ThreadPoolExecutor() as executor:
            #

                # candle_start = datetime.datetime.today().strftime('%Y-%m-%d')
                # tasks.append(self._fetch_board_candles(
                #     session, tiker=tiker, start=candle_start))

            # results = await asyncio.gather(*tasks)

            # data = results[0]
            # candles = results[1]
            if add_current and data and candles:
                last_candle = candles[-1]
                last_data = {
                    "OPEN": last_candle.get('open'),
                    "CLOSE": last_candle.get('close'),
                    "LOW": last_candle.get('low'),
                    "HIGH": last_candle.get('high'),
                    "VALUE": last_candle.get('value'),
                    "VOLUME": last_candle.get('volume'),
                    "TRADEDATE": candle_start
                }

                if candle_start == data[-1]['TRADEDATE']:
                    data[-1] = last_data
                else:
                    data.append(last_data)

            df = DataFrame(data)
            if df.size > 0:
                df['TRADEDATE'] = pd.to_datetime(df['TRADEDATE'])
                df.set_index('TRADEDATE', inplace=True)
            return df
