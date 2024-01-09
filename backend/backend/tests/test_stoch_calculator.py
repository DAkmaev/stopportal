import contextlib
import time
from pathlib import Path

import pytest
import pandas as pd
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.db.dao.companies import CompanyDAO
from backend.services.stoch_service import StochService
from backend.tests.utils.common import create_test_company, create_test_companies
from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionDTO
from backend.db.models.company import StopModel

from unittest.mock import patch


@pytest.fixture
def sample_dataframe():
    file_path = Path(__file__).parent / 'data/mocked_data.csv'
    df = pd.read_csv(file_path)
    df['DATE'] = pd.to_datetime(df['DATE'])  # Convert DATE column to datetime
    df.set_index('DATE', inplace=True)  # Set DATE as the index
    df = df.rename(
        columns={'OPEN': 'OPEN', 'CLOSE': 'CLOSE', 'HIGH': 'HIGH', 'LOW': 'LOW'})

    return df


@pytest.fixture
def sample_lkoh_dataframe():
    file_path = Path(__file__).parent / 'data/mocked_lkoh_history.csv'
    df = pd.read_csv(file_path)
    df['DATE'] = pd.to_datetime(df['DATE'])  # Convert DATE column to datetime
    df.set_index('DATE', inplace=True)  # Set DATE as the index
    df = df.rename(
        columns={'OPEN': 'OPEN', 'CLOSE': 'CLOSE', 'HIGH': 'HIGH', 'LOW': 'LOW'})

    return df


@pytest.fixture
def sample_stoch_dataframe():
    file_path = Path(__file__).parent / 'data/mocked_stoch_data.csv'
    df = pd.read_csv(file_path)
    df['DATE'] = pd.to_datetime(df['DATE'])  # Convert DATE column to datetime
    df.set_index('DATE', inplace=True)  # Set DATE as the index
    df = df.rename(columns={'k': 'k', 'd': 'd'})

    return df


@contextlib.contextmanager
def report_time(test):
    print("\n")
    t0 = time.time()
    yield
    print("Time needed for `%s' called: %.2fs"
          % (test, time.time() - t0))


class MockMoexReader:
    @staticmethod
    async def get_company_history(start, ticker):
        return sample_dataframe


@pytest.mark.anyio
async def test_get_period_decision(sample_dataframe):
    calculator = StochCalculator()

    # Test with a sample DataFrame
    decision = calculator._get_period_decision(sample_dataframe, 'D')

    assert decision.decision in {StochDecisionEnum.BUY, StochDecisionEnum.SELL,
                                 StochDecisionEnum.RELAX}
    assert isinstance(decision.df, pd.DataFrame)


@pytest.mark.anyio
async def test_calculate_decision(sample_dataframe, dbsession: AsyncSession):
    calculator = StochCalculator()
    period = 'D'
    last_price = 130.0
    stop = StopModel(period='D', value=120.0)

    # Создаем тестовую компанию и
    company = await create_test_company(dbsession)

    decision = calculator._calculate_decision(company, period, sample_dataframe,
                                              stop, last_price)

    assert decision.decision in {StochDecisionEnum.BUY, StochDecisionEnum.SELL,
                                 StochDecisionEnum.RELAX}
    assert isinstance(decision.k, float)
    assert isinstance(decision.d, float)
    assert isinstance(decision.last_price, float)
    assert decision.company.tiker == company.tiker


@pytest.mark.anyio
async def test_get_stoch_decisions_no_data(dbsession: AsyncSession):
    calculator = StochCalculator()
    period = 'D'

    # Создаем тестовую компанию и
    company = await create_test_company(dbsession)

    # Simulate the case where there's no data available
    decisions = calculator.get_company_stoch_decisions(company, period)

    assert isinstance(decisions, dict)
    assert isinstance(decisions[period], StochDecisionDTO)
    assert decisions[period].decision == StochDecisionEnum.UNKNOWN
    assert decisions[period].company.tiker == company.tiker


@pytest.mark.anyio
async def test_get_stoch_decisions_with_stop(sample_dataframe, dbsession: AsyncSession):
    calculator = StochCalculator()
    period = 'D'
    stop = StopModel(period='D', value=120.0)

    # Создаем тестовую компанию и
    company = await create_test_company(dbsession)
    company.stops.append(stop)

    # Mock the mreader.get_company_history_async to return sample_dataframe
    with patch(
        'backend.utils.moex.moex_reader.MoexReader.get_company_history') as mock_method:
        mock_method.return_value = sample_dataframe
        decisions = calculator.get_company_stoch_decisions(company, period)

        assert isinstance(decisions, dict)
        assert isinstance(decisions[period], StochDecisionDTO)
        assert decisions[period].decision.name == StochDecisionEnum.SELL
        assert decisions[period].company.tiker == company.tiker


@pytest.mark.anyio
async def test_get_stoch_decisions(sample_dataframe, sample_stoch_dataframe,
                                   dbsession: AsyncSession):
    calculator = StochCalculator()
    period = 'ALL'

    with report_time("Create companies"):
        companies = await create_test_companies(dbsession, 10)

    with (
        patch(
            'backend.utils.moex.moex_reader.MoexReader.get_company_history') as mock_method,
        patch(
            'backend.utils.stoch.stoch_calculator.StochCalculator._generate_stoch_df') as mock_stoch
    ):
        #  значений назад цифры подходящие для покупки
        mock_method.return_value = sample_dataframe
        mock_stoch.return_value = sample_stoch_dataframe

        with report_time("Generate decisions"):
            decisions = await calculator.get_companies_stoch_decisions(companies,
                                                                       period)
            assert len(decisions) == 10

@pytest.mark.anyio
async def test_get_stoch(
    sample_lkoh_dataframe,
    fastapi_app: FastAPI,
    dbsession: AsyncSession
) -> None:

    calculator = StochCalculator()
    stoch_D = calculator.get_stoch(sample_lkoh_dataframe, 'D')
    stoch_W = calculator.get_stoch(sample_lkoh_dataframe, 'W')
    stoch_M = calculator.get_stoch(sample_lkoh_dataframe, 'M')

    assert stoch_D.size != 0
    assert stoch_W.size != 0
    assert stoch_M.size != 0


# @pytest.mark.anyio
# async def test_get_history_stochs(
#     sample_lkoh_dataframe,
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     dbsession: AsyncSession
# ) -> None:
#     company = await create_test_company(dbsession, tiker_name='LKOH')
#     with patch('backend.utils.moex.moex_reader.MoexReader.get_company_history') as mock_method:
#         mock_method.return_value = sample_lkoh_dataframe
#         #mock_method.return_value = sample_lkoh_dataframe.iloc[:-1980]
#         #mock_method.return_value = sample_lkoh_dataframe.iloc[:-2014]
#
#
#         url = fastapi_app.url_path_for("get_history_stochs", tiker=company.tiker)
#         response = await client.get(url)
#
#         assert response.status_code == status.HTTP_200_OK
