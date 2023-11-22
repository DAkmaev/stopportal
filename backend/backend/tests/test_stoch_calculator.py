from pathlib import Path

import pytest
import pandas as pd

from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionModel
from backend.db.models.company import StopModel

from unittest.mock import patch


@pytest.fixture
def sample_dataframe():
    file_path = Path(__file__).parent / 'data/mocked_data.csv'
    df = pd.read_csv(file_path)
    df['DATE'] = pd.to_datetime(df['DATE'])  # Convert DATE column to datetime
    df.set_index('DATE', inplace=True)  # Set DATE as the index
    df = df.rename(columns={'OPEN': 'OPEN', 'CLOSE': 'CLOSE', 'HIGH': 'HIGH', 'LOW': 'LOW'})

    return df


class MockMoexReader:
    @staticmethod
    async def get_company_history(start, ticker):
        return sample_dataframe


@pytest.mark.anyio
async def test_get_period_decision(sample_dataframe):
    calculator = StochCalculator()

    # Test with a sample DataFrame
    decision = await calculator._get_period_decision(sample_dataframe, 'D')

    assert decision.decision in {StochDecisionEnum.BUY, StochDecisionEnum.SELL,
                                 StochDecisionEnum.RELAX}
    assert isinstance(decision.df, pd.DataFrame)


@pytest.mark.anyio
async def test_calculate_decision(sample_dataframe):
    calculator = StochCalculator()
    tiker = 'LKOH'
    period = 'D'
    last_price = 130.0
    stop = StopModel(period='D', value=120.0)

    decision = await calculator._calculate_decision(tiker, period, sample_dataframe,
                                                    stop, last_price)

    assert decision.decision in {StochDecisionEnum.BUY, StochDecisionEnum.SELL,
                                 StochDecisionEnum.RELAX}
    assert isinstance(decision.k, float)
    assert isinstance(decision.d, float)
    assert isinstance(decision.last_price, float)
    assert decision.tiker == tiker


@pytest.mark.anyio
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


@pytest.mark.anyio
async def test_get_stoch_decisions_with_stop(sample_dataframe):
    calculator = StochCalculator()
    tiker = 'LKOH'
    tiker_type = 'MOEX'
    period = 'D'
    stop = StopModel(period='D', value=120.0)

    # Mock the mreader.get_company_history_async to return sample_dataframe
    with patch('backend.utils.moex.moex_reader.MoexReader.get_company_history_async') as mock_method:
        mock_method.return_value = sample_dataframe
        decisions = await calculator.get_stoch_decisions(tiker, tiker_type, period, [stop])

        assert isinstance(decisions, dict)
        assert isinstance(decisions[period], StochDecisionModel)
        assert decisions[period].decision == StochDecisionEnum.SELL
        assert decisions[period].stop == stop.value
        assert decisions[period].tiker == tiker


# @pytest.mark.asyncio
# async def test_get_stoch_decisions_buy(sample_dataframe):
#     calculator = StochCalculator()
#     tiker = 'LKOH'
#     tiker_type = 'MOEX'
#     period = 'M'
#
#     with patch('backend.utils.moex.moex_reader.MoexReader.get_company_history_async') as mock_method:
#         #  значений назад цифры подходящие для покупки
#         mock_method.return_value = sample_dataframe #.iloc[:-0]
#         # Simulate a case where the conditions suggest a buy
#         decisions = await calculator.get_stoch_decisions(tiker, tiker_type, period, [])
#
#         assert decisions == {
#             'M': StochDecisionEnum.BUY,
#             'W': StochDecisionEnum.BUY,
#             'D': StochDecisionEnum.BUY,
#         }

