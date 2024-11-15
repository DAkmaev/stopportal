import contextlib
import time
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from pandas import DataFrame

from server.src.schemas.company import  CompanyStopDTO
from server.src.utils.ta.ta_calculator import TACalculator
from server.src.schemas.ta import DecisionEnum, CompanyDTO, DecisionDTO


@pytest.fixture
def sample_dataframe():
    file_path = Path(__file__).parent.parent / "data/mocked_data.csv"
    df = pd.read_csv(file_path)
    df["DATE"] = pd.to_datetime(df["DATE"])  # Convert DATE column to datetime
    df.set_index("DATE", inplace=True)  # Set DATE as the index
    df = df.rename(
        columns={"OPEN": "OPEN", "CLOSE": "CLOSE", "HIGH": "HIGH", "LOW": "LOW"}
    )

    return df


@pytest.fixture
def sample_lkoh_dataframe():
    file_path = Path(__file__).parent.parent / "data/mocked_lkoh_history.csv"
    df = pd.read_csv(file_path)
    df["DATE"] = pd.to_datetime(df["DATE"])  # Convert DATE column to datetime
    df.set_index("DATE", inplace=True)  # Set DATE as the index
    df = df.rename(
        columns={"OPEN": "OPEN", "CLOSE": "CLOSE", "HIGH": "HIGH", "LOW": "LOW"}
    )

    return df


@pytest.fixture
def sample_stoch_dataframe():
    file_path = Path(__file__).parent.parent / "data/mocked_stoch_data.csv"
    df = pd.read_csv(file_path)
    df["DATE"] = pd.to_datetime(df["DATE"])  # Convert DATE column to datetime
    df.set_index("DATE", inplace=True)  # Set DATE as the index
    df = df.rename(columns={"k": "k", "d": "d"})

    return df


@contextlib.contextmanager
def report_time(test):
    print("\n")
    t0 = time.time()
    yield
    print(f"Time needed for `{test}' called: {time.time() - t0}%")


class MockMoexReader:
    @staticmethod
    async def get_company_history(start, ticker):
        return sample_dataframe


def test_get_period_decision(sample_dataframe):
    calculator = TACalculator()

    # Test with a sample DataFrame
    decision = calculator._get_period_decision(sample_dataframe, "D")

    assert decision.decision in {
        DecisionEnum.BUY,
        DecisionEnum.SELL,
        DecisionEnum.RELAX,
    }
    assert isinstance(decision.df, pd.DataFrame)


def test_calculate_decision(sample_dataframe):
    calculator = TACalculator()
    period = "D"
    last_price = 130.0

    company = CompanyDTO(
        name="Test", tiker="TST", stops=[ CompanyStopDTO(period=period, value=120.0)]
    )

    decision = calculator._calculate_decision(
        company, period, sample_dataframe, last_price
    )

    assert decision.decision in {
        DecisionEnum.BUY,
        DecisionEnum.SELL,
        DecisionEnum.RELAX,
    }
    assert isinstance(decision.k, float)
    assert isinstance(decision.d, float)
    assert isinstance(decision.last_price, float)
    assert decision.tiker == company.tiker


@patch("server.src.utils.moex.moex_reader.MoexReader.get_company_history")
def test_get_stoch_decisions_no_data(
    mock_get_company_history,
):
    mock_get_company_history.return_value = DataFrame()

    calculator = TACalculator()
    period = "D"

    company = CompanyDTO(name="Test", tiker="TST")

    # Simulate the case where there's no data available
    decisions = calculator.get_company_ta_decisions(company, period)

    assert isinstance(decisions, dict)
    assert isinstance(decisions[period], DecisionDTO)
    assert decisions[period].decision == DecisionEnum.UNKNOWN
    assert decisions[period].tiker == company.tiker


@patch("server.src.utils.moex.moex_reader.MoexReader.get_company_history")
def test_get_stoch_decisions_with_stop(
    mock_get_company_history,
    sample_dataframe,
):
    mock_get_company_history.return_value = sample_dataframe

    calculator = TACalculator()
    period = "D"
    value = 120.0

    company = CompanyDTO(
        name="Test", tiker="TST", stops=[ CompanyStopDTO(period=period, value=value)]
    )

    decisions = calculator.get_company_ta_decisions(company, period)

    assert isinstance(decisions, dict)
    assert isinstance(decisions[period], DecisionDTO)
    assert decisions[period].decision.name == DecisionEnum.SELL
    assert decisions[period].tiker == company.tiker


def test_get_stoch(
    sample_lkoh_dataframe,
) -> None:

    calculator = TACalculator()
    with report_time("Get ta"):
        stoch_D = calculator.generate_ta_indicators(sample_lkoh_dataframe, "D")
        stoch_W = calculator.generate_ta_indicators(sample_lkoh_dataframe, "W")
        stoch_M = calculator.generate_ta_indicators(sample_lkoh_dataframe, "M")

        assert stoch_D.size != 0
        assert stoch_W.size != 0
        assert stoch_M.size != 0

        # Проверяем последнюю строку
        assert stoch_D.iloc[-1]["k"] == 55.0951118966398
        assert stoch_D.iloc[-1]["d"] == 52.04061579315601

        assert stoch_W.iloc[-1]["k"] == 34.344579818736555
        assert stoch_W.iloc[-1]["d"] == 35.581577728133325

        assert stoch_M.iloc[-1]["k"] == 83.15564413051169
        assert stoch_M.iloc[-1]["d"] == 87.04591638759291
