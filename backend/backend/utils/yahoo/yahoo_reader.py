import btalib
import yahoo_fin.stock_info as si
from pandas import DataFrame


class YahooReader:
    def get_company_history(self, start: str, tiker: str) -> DataFrame:
        # pull data from Yahoo Finance
        data = si.get_data(tiker, start_date=start)

        # #print(data_y)
        stoch = btalib.stochastic(data)

        # print(stoch.df)
        return stoch

