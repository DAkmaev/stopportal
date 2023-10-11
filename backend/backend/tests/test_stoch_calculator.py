Аfrom pathlib import Path

import pandas as pd
import pytest

from backend.utils.stoch.stoch_calculator import StochCalculator, StochDecision
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionModel
from backend.web.api.company.scheme import CompanyTypeEnum


# Mocked data for testing
def load_mocked_data():
    file_path = Path(__file__).parent / 'data/mocked_data.csv'
    return pd.read_csv(file_path)

mocked_dataframe = load_mocked_data()
mocked_ticker = "LKOH"
mocked_type = CompanyTypeEnum.MOEX
mocked_period = "D"
mocked_stop = None


class MockMoexReader:
    @staticmethod
    async def get_company_history(start, ticker):
        return mocked_dataframe


class MockYahooReader:
    @staticmethod
    async def get_company_history(start, ticker):
        return mocked_dataframe


@pytest.mark.anyio
async def test_get_period_decision():
    calculator = StochCalculator()
    stoch_decision = await calculator.get_period_decision(mocked_dataframe, period="D")

    assert isinstance(stoch_decision, StochDecision)
    assert stoch_decision.decision in [StochDecisionEnum.BUY, StochDecisionEnum.SELL, StochDecisionEnum.RELAX]


@pytest.mark.anyio
async def test_get_stoch_decision(monkeypatch):
    # Mocking the external calls to MoexReader and YahooReader
    monkeypatch.setattr("backend.utils.moex.moex_reader.MoexReader", MockMoexReader)
    monkeypatch.setattr("backend.utils.yahoo.yahoo_reader.YahooReader", MockYahooReader)

    calculator = StochCalculator()
    stoch_decision = await calculator.get_stoch_decision(mocked_ticker, mocked_type, mocked_period, mocked_stop)

    assert isinstance(stoch_decision, StochDecisionModel)
    assert stoch_decision.decision in [StochDecisionEnum.BUY, StochDecisionEnum.SELL, StochDecisionEnum.RELAX]
    assert isinstance(stoch_decision.k, float)
    assert isinstance(stoch_decision.d, float)
    assert isinstance(stoch_decision.last_price, float)
    assert stoch_decision.tiker == mocked_ticker


# @pytest.mark.anyio
# async def test_get_stoch_decision_bye(monkeypatch):
#     # Mocking the external calls to MoexReader and YahooReader
#     monkeypatch.setattr("backend.utils.moex.moex_reader.MoexReader", MockMoexReader)
#     monkeypatch.setattr("backend.utils.yahoo.yahoo_reader.YahooReader", MockYahooReader)
#
#     calculator = StochCalculator()
#     stoch_decision = await calculator.get_stoch_decision(mocked_ticker, mocked_type, 'D', None)
#
#     assert isinstance(stoch_decision, StochDecisionModel)
#     assert stoch_decision.decision == StochDecisionEnum.BUY
#
# @pytest.mark.anyio
# async def test_get_stoch_decision_bye(monkeypatch):
#     # Mocking the external calls to MoexReader and YahooReader
#     monkeypatch.setattr("backend.utils.moex.moex_reader.MoexReader", MockMoexReader)
#     monkeypatch.setattr("backend.utils.yahoo.yahoo_reader.YahooReader", MockYahooReader)
#
#     calculator = StochCalculator()
#     stoch_decision = await calculator.get_stoch_decision(mocked_ticker, mocked_type, 'D', None)
#
#     assert isinstance(stoch_decision, StochDecisionModel)
#     assert stoch_decision.decision == StochDecisionEnum.BUY
