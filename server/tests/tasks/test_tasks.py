from unittest.mock import patch

import pytest

from server.src.schemas.company import CompanyDTO
from server.src.schemas.enums import PeriodEnum, DecisionEnum
from server.src.schemas.ta import (
    TAStartGenerateMessage,
    TAFinalMessage,
    TAGenerateMessage,
    DecisionDTO,
)
from server.src.worker.tasks import (
    start_generate_task,
    ta_generate_task,
    ta_final_task,
    send_telegram_task,
)


@pytest.mark.integrations
def test_start_generate_task(celery_local_app):
    payload_obj = TAStartGenerateMessage(
        user_id=1,
        period=PeriodEnum.DAY,
        companies=[],
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
@patch("server.src.worker.tasks.send_sync_tg_message")
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


@patch("server.src.worker.tasks.send_sync_tg_message")
def test_send_telegram_task(
        mock_send_sync_tg_message,
        celery_app,
):
    mock_send_sync_tg_message.return_value = ""
    payload_str = "Test message"
    result = send_telegram_task.apply(args=(payload_str,))
    assert result.successful()
