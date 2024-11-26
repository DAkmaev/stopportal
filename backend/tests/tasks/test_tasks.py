from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.dao.ta_decisions import TADecisionDAO
from backend.app.schemas.company import CompanyDTO, CompanyStopDTO
from backend.app.schemas.enums import PeriodEnum, DecisionEnum
from backend.app.schemas.ta import (
    TAStartGenerateMessage,
    TAFinalMessage,
    TAGenerateMessage,
    DecisionDTO,
)
from backend.app.worker.tasks import (
    start_generate_task,
    ta_generate_task,
    ta_final_task,
    send_telegram_task,
    update_db_decisions,
)
from backend.tests.utils.common import create_test_user, create_test_company


@pytest.mark.integrations
def test_start_generate_task(celery_local_app):
    companies = [
        CompanyDTO(
            name="Test1",
            tiker="TST1",
        ),
        CompanyDTO(
            name="Test1",
            tiker="TST1",
            stops=[
                CompanyStopDTO(
                    period=PeriodEnum.DAY,
                    value=100.0,
                )
            ],
        ),
    ]
    payload_obj = TAStartGenerateMessage(
        user_id=1,
        period=PeriodEnum.DAY,
        companies=companies,
    )
    payload_str = str(payload_obj.model_dump_json())
    result = start_generate_task.apply(args=(payload_str,))

    assert result.status in ("PENDING", "SUCCESS")


def test_ta_generate_task(celery_local_app):
    tiker = "TST"
    name = "Test"
    period = PeriodEnum.DAY
    payload_obj = TAGenerateMessage(
        period=period,
        company=CompanyDTO(name=name, tiker=tiker),
    )
    user_id = 1
    payload_str = str(payload_obj.model_dump_json())
    result = ta_generate_task.apply(
        args=(
            payload_str,
            user_id,
        )
    )

    assert result.successful()
    decision = DecisionDTO.model_validate_json(result.result[0])
    assert decision.tiker == tiker
    assert decision.period == period
    assert decision.decision == DecisionEnum.UNKNOWN


@pytest.mark.integrations
@patch("backend.app.worker.tasks.send_sync_tg_message")
def test_final_task(celery_app):
    payload_obj = TAFinalMessage(
        user_id=1,
        send_message=True,
        update_db=False,
        send_test_message=True,
    )
    payload_str = str(payload_obj.model_dump_json())

    decisions: list[DecisionDTO] = [
        DecisionDTO(
            tiker="TST",
            decision=DecisionEnum.SELL,
            period=PeriodEnum.DAY,
            last_price=100.0,
            k=50.0,
            d=50.0,
        )
    ]
    results_str = [[dec.model_dump_json() for dec in decisions]]

    result = ta_final_task.apply(
        args=(
            results_str,
            payload_str,
        )
    )

    assert result.successful()


@patch("backend.app.worker.tasks.update_db_decisions")
@pytest.mark.integrations
@pytest.mark.anyio
async def test_final_task_update_db(
    mock_update_db_decisions,
    celery_app,
    dbsession: AsyncSession,
):
    mock_update_db_decisions.return_value = "TEST_UPDATE"
    user = await create_test_user(dbsession)
    company = await create_test_company(dbsession, user_id=user.id)
    ts_dao = TADecisionDAO(dbsession)

    payload_obj = TAFinalMessage(
        user_id=user.id,
        send_message=False,
        update_db=True,
        send_test_message=False,
    )
    payload_str = str(payload_obj.model_dump_json())

    decisions: list[DecisionDTO] = [
        DecisionDTO(
            tiker=company.tiker,
            decision=DecisionEnum.SELL,
            period=PeriodEnum.DAY,
            last_price=100.0,
            k=50.0,
            d=50.0,
        )
    ]
    results_str = [[dec.model_dump_json() for dec in decisions]]

    result = ta_final_task.apply(
        args=(
            results_str,
            payload_str,
        )
    )

    assert result.successful()


@pytest.mark.anyio
async def test_update_db_decisions(
    dbsession: AsyncSession,
):
    user = await create_test_user(dbsession)
    company = await create_test_company(dbsession, user_id=user.id)
    ts_dao = TADecisionDAO(dbsession)

    decisions: list[DecisionDTO] = [
        DecisionDTO(
            tiker=company.tiker,
            decision=DecisionEnum.SELL,
            period=PeriodEnum.DAY,
            last_price=100.0,
            k=50.0,
            d=50.0,
        )
    ]

    result = await update_db_decisions(
        decisions=decisions, user_id=user.id, dbsession=dbsession
    )

    assert result is None
    ta_decisions = await ts_dao.get_ta_decision_models()
    assert len(ta_decisions) == 1
    assert ta_decisions[0].decision == DecisionEnum.SELL


@patch("backend.app.worker.tasks.send_sync_tg_message")
def test_send_telegram_task(
    mock_send_sync_tg_message,
    celery_app,
):
    mock_send_sync_tg_message.return_value = ""
    payload_str = "Test message"
    result = send_telegram_task.apply(args=(payload_str,))
    assert result.successful()
