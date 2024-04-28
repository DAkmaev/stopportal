import contextlib
import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pandas as pd
import pytest
from httpx import AsyncClient
from pandas import DataFrame

from app.db.models.company import StopModel
from app.schemas.ta import TADecisionEnum, TADecisionDTO
from app.tests.utils.common import (
    create_test_companies,
    create_test_company,
    create_test_user,
)
from app.utils.ta.ta_sync_calculator import TACalculator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def sample_dataframe():
    file_path = Path(__file__).parent / "data/mocked_data.csv"
    df = pd.read_csv(file_path)
    df["DATE"] = pd.to_datetime(df["DATE"])  # Convert DATE column to datetime
    df.set_index("DATE", inplace=True)  # Set DATE as the index
    df = df.rename(
        columns={"OPEN": "OPEN", "CLOSE": "CLOSE", "HIGH": "HIGH", "LOW": "LOW"}
    )

    return df


@pytest.fixture
def sample_lkoh_dataframe():
    file_path = Path(__file__).parent / "data/mocked_lkoh_history.csv"
    df = pd.read_csv(file_path)
    df["DATE"] = pd.to_datetime(df["DATE"])  # Convert DATE column to datetime
    df.set_index("DATE", inplace=True)  # Set DATE as the index
    df = df.rename(
        columns={"OPEN": "OPEN", "CLOSE": "CLOSE", "HIGH": "HIGH", "LOW": "LOW"}
    )

    return df


@pytest.fixture
def sample_stoch_dataframe():
    file_path = Path(__file__).parent / "data/mocked_stoch_data.csv"
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


@pytest.mark.anyio
async def test_get_period_decision(sample_dataframe):
    calculator = TACalculator()

    # Test with a sample DataFrame
    decision = calculator._get_period_decision(sample_dataframe, "D")

    assert decision.decision in {
        TADecisionEnum.BUY,
        TADecisionEnum.SELL,
        TADecisionEnum.RELAX,
    }
    assert isinstance(decision.df, pd.DataFrame)


@pytest.mark.anyio
async def test_calculate_decision(sample_dataframe, dbsession: AsyncSession):
    calculator = TACalculator()
    period = "D"
    last_price = 130.0
    stop = StopModel(period="D", value=120.0)

    # Создаем тестовую компанию и
    company = await create_test_company(dbsession)

    decision = calculator._calculate_decision(
        company, period, sample_dataframe, last_price
    )

    assert decision.decision in {
        TADecisionEnum.BUY,
        TADecisionEnum.SELL,
        TADecisionEnum.RELAX,
    }
    assert isinstance(decision.k, float)
    assert isinstance(decision.d, float)
    assert isinstance(decision.last_price, float)
    assert decision.company.tiker == company.tiker


@pytest.mark.anyio
@patch("app.utils.moex.moex_reader.MoexReader.get_company_history")
async def test_get_stoch_decisions_no_data(
    mock_get_company_history, dbsession: AsyncSession
):
    mock_get_company_history.return_value = DataFrame()

    calculator = TACalculator()
    period = "D"

    # Создаем тестовую компанию и
    company = await create_test_company(dbsession)

    # Simulate the case where there's no data available
    decisions = calculator.get_company_ta_decisions(company, period)

    assert isinstance(decisions, dict)
    assert isinstance(decisions[period], TADecisionDTO)
    assert decisions[period].decision == TADecisionEnum.UNKNOWN
    assert decisions[period].company.tiker == company.tiker


@pytest.mark.anyio
@patch("app.utils.moex.moex_reader.MoexReader.get_company_history")
async def test_get_stoch_decisions_with_stop(
    mock_get_company_history, sample_dataframe, dbsession: AsyncSession
):
    mock_get_company_history.return_value = sample_dataframe

    calculator = TACalculator()
    period = "D"
    stop = StopModel(period="D", value=120.0)

    # Создаем тестовую компанию и
    company = await create_test_company(dbsession)
    company.stops.append(stop)

    decisions = calculator.get_company_ta_decisions(company, period)

    assert isinstance(decisions, dict)
    assert isinstance(decisions[period], TADecisionDTO)
    assert decisions[period].decision.name == TADecisionEnum.SELL
    assert decisions[period].company.tiker == company.tiker


@pytest.mark.anyio
async def test_get_stoch(
    sample_lkoh_dataframe, fastapi_app: FastAPI, dbsession: AsyncSession
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


# @pytest.mark.anyio
# async def test_get_history_stochs(
#     sample_lkoh_dataframe,
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     dbsession: AsyncSession
# ) -> None:
#     company = await create_test_company(dbsession, tiker_name='LKOH')
#     with patch('app.utils.moex.moex_reader.MoexReader.get_company_history') as mock_method:
#         mock_method.return_value = sample_lkoh_dataframe
#         #mock_method.return_value = sample_lkoh_dataframe.iloc[:-1980]
#         #mock_method.return_value = sample_lkoh_dataframe.iloc[:-2014]
#
#
#         url = fastapi_app.url_path_for("get_history_stochs", tiker=company.tiker)
#         response = await client.get(url)
#
#         assert response.status_code == status.HTTP_200_OK
