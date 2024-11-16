import yahoo_fin as si
from pandas import DataFrame


class YahooReader:
    def get_company_history(self, start: str, tiker: str) -> DataFrame:
        # pull data from Yahoo Finance
        return si.stock_info.get_data(tiker, start_date=start)
