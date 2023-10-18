# import datetime
# from unittest.mock import MagicMock
# import pandas as pd
# import pytest
# from pandas._testing import assert_frame_equal
# from backend.utils.moex.moex_reader import MoexReader
#
# @pytest.fixture
# async def mock_requests_get(monkeypatch):
#     mock_response = MagicMock()
#     mock_response.json.return_value = [
#         {
#             "open": 100.0,
#             "high": 110.0,
#             "low": 90.0,
#             "boardid": "TQBR",
#             "tradedate": "2023-10-10",
#             "close": 105.0,
#             "volume": 1000,
#             "value": 100000.0
#         }
#     ]
#     monkeypatch.setattr("backend.utils.moex.moex_reader.apimoex.get_board_history", lambda *args, **kwargs: mock_response)
#     return mock_response
#
# @pytest.mark.asyncio
# async def test_get_company_history(mock_requests_get):
#     start_date = datetime.datetime(2023, 10, 10)
#     tiker = "AAPL"
#
#     expected_data = {
#         "OPEN": [100.0],
#         "HIGH": [110.0],
#         "LOW": [90.0],
#         "BOARDID": ["TQBR"],
#         "TRADEDATE": [datetime.datetime(2023, 10, 10)],
#         "CLOSE": [105.0],
#         "VOLUME": [1000],
#         "VALUE": [100000.0]
#     }
#
#     expected_df = pd.DataFrame(expected_data)
#     expected_df["TRADEDATE"] = pd.to_datetime(expected_df["TRADEDATE"])
#     expected_df.set_index("TRADEDATE", inplace=True)
#
#     # Call the method under test
#     moex_reader = MoexReader()
#     result_df = await moex_reader.get_company_history_async(start=start_date, tiker=tiker)
#
#     # Ensure the returned DataFrame matches the expected DataFrame
#     assert_frame_equal(result_df, expected_df)
#
# if __name__ == "__main__":
#     pytest.main()
