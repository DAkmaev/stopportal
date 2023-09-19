import datetime

import apimoex
import pandas as pd
import requests
from pandas import DataFrame


class MoexReader:
    def get_stock_history(start: datetime, tiker: str) -> DataFrame:
        COLUMNS = (
            "OPEN",
            "HIGH",
            "LOW",
            "BOARDID",
            "TRADEDATE",
            "CLOSE",
            "VOLUME",
            "VALUE",
        )
        with requests.Session() as session:
            data = apimoex.get_board_history(
                session, tiker, start=str(start), columns=COLUMNS)

            df = pd.DataFrame(data)

            # Преобразовываем столбец TRADEDATE в тип datetime
            df['TRADEDATE'] = pd.to_datetime(df['TRADEDATE'])

            # Устанавливаем столбец TRADEDATE в качестве индекса
            df.set_index('TRADEDATE', inplace=True)

            return df
