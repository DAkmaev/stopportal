import datetime

import apimoex
import pandas as pd
import requests
from pandas import DataFrame


class MoexReader:
    def get_company_history(start: datetime, tiker: str, add_current: bool = True) -> DataFrame:
        COLUMNS = (
            "OPEN",
            "HIGH",
            "LOW",
            "TRADEDATE",
            "CLOSE",
            "VOLUME",
            "VALUE",
        )
        with requests.Session() as session:
            data = apimoex.get_board_history(
                session, tiker, start=str(start), columns=COLUMNS)

            if add_current:
                candle_start = datetime.datetime.today().strftime('%Y-%m-%d')
                candles = apimoex.get_board_candles(
                    session,security=tiker, interval=10, start=candle_start, columns=None)

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

                print(data)

            df = pd.DataFrame(data)

            if df.size > 0:
                # Преобразовываем столбец TRADEDATE в тип datetime
                df['TRADEDATE'] = pd.to_datetime(df['TRADEDATE'])

                # Устанавливаем столбец TRADEDATE в качестве индекса
                df.set_index('TRADEDATE', inplace=True)

            return df
