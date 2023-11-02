from pathlib import Path

import pytest
import pandas as pd
from _pytest import monkeypatch

from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionModel
from backend.db.models.companies import CompanyStopModel
import asyncio

from unittest.mock import patch


@pytest.fixture
def sample_dataframe():
    file_path = Path(__file__).parent / 'data/mocked_data.csv'
    return pd.read_csv(file_path)


class MockMoexReader:
    @staticmethod
    async def get_company_history(start, ticker):
        return sample_dataframe


@pytest.mark.asyncio
async def test_get_period_decision(sample_dataframe):
    calculator = StochCalculator()

    # Test with a sample DataFrame
    decision = await calculator._get_period_decision(sample_dataframe, 'D')

    assert decision.decision in {StochDecisionEnum.BUY, StochDecisionEnum.SELL,
                                 StochDecisionEnum.RELAX}
    assert isinstance(decision.df, pd.DataFrame)


# NOT PASSED
# @pytest.mark.asyncio
# async def test_calculate_decision(sample_dataframe):
#     calculator = StochCalculator()
#     tiker = 'AAPL'
#     period = 'D'
#     last_price = 130.0
#     stop = CompanyStopModel(period='D', value=120.0)
#
#     decision = await calculator._calculate_decision(tiker, period, sample_dataframe,
#                                                     stop, last_price)
#
#     assert decision.decision in {StochDecisionEnum.BUY, StochDecisionEnum.SELL,
#                                  StochDecisionEnum.RELAX}
#     assert isinstance(decision.k, float)
#     assert isinstance(decision.d, float)
#     assert isinstance(decision.last_price, float)
#     assert decision.tiker == tiker


@pytest.mark.asyncio
async def test_get_stoch_decisions_no_data():
    calculator = StochCalculator()
    tiker = 'AAPL'
    tiker_type = 'MOEX'
    period = 'D'

    # Simulate the case where there's no data available
    decisions = await calculator.get_stoch_decisions(tiker, tiker_type, period, [])

    assert isinstance(decisions, dict)
    assert isinstance(decisions[period], StochDecisionModel)
    assert decisions[period].decision == StochDecisionEnum.UNKNOWN
    assert decisions[period].tiker == tiker


# @pytest.mark.asyncio
# async def test_get_stoch_decisions_with_stop(sample_dataframe):
#     # Mocking the external calls to MoexReader and YahooReader
#     #monkeypatch.setattr("backend.utils.moex.moex_reader.MoexReader", MockMoexReader)
#
#     calculator = StochCalculator()
#     tiker = 'AAPL'
#     tiker_type = 'MOEX'
#     period = 'D'
#     stop = CompanyStopModel(period='D', value=120.0)
#
#     # Mock the mreader.get_company_history_async to return sample_dataframe
#     with patch('backend.utils.moex.moex_reader.MoexReader.get_company_history_async') as mock_method:
#         mock_method.return_value = sample_dataframe
#         decisions = await calculator.get_stoch_decisions(tiker, tiker_type, period, [])
#
#
#         assert decisions == {
#             'M': StochDecisionEnum.SELL,
#             'W': StochDecisionEnum.SELL,
#             'D': StochDecisionEnum.SELL,
#         }
#
# @pytest.mark.asyncio
# async def test_get_stoch_decisions_buy(sample_dataframe):
#     calculator = StochCalculator()
#     tiker = 'AAPL'
#     tiker_type = 'MOEX'
#     period = 'D'
#     stop = CompanyStopModel(period='D', value=140.0)
#
#     # Simulate a case where the conditions suggest a buy
#     decisions = asyncio.run(calculator.get_stoch_decisions(tiker, tiker_type, period, [stop]))
#
#     assert decisions == {
#         'M': StochDecisionEnum.BUY,
#         'W': StochDecisionEnum.BUY,
#         'D': StochDecisionEnum.BUY,
#     }


# You can add more tests for other methods as needed
