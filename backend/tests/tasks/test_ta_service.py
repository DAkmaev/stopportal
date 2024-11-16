from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.ta_service import TAService
from backend.app.schemas.company import CompanyDTO
from backend.app.schemas.enums import DecisionEnum, PeriodEnum
from backend.app.schemas.ta import DecisionDTO
from backend.tests.utils.common import (
    create_test_company,
    create_test_briefcase,
    create_test_briefcase_share,
)


@pytest.mark.anyio
async def test_generate_bulk_tg_messages(
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()
    company1 = await create_test_company(dbsession, user_id=user.id)
    company2 = await create_test_company(dbsession, user_id=user.id)
    briefcase = await create_test_briefcase(dbsession, user_id=user.id)

    company1_dto = CompanyDTO(
        id=company1.id,
        name=company1.name,
        tiker=company1.tiker,
    )
    company2_dto = CompanyDTO(
        id=company2.id,
        name=company2.name,
        tiker=company2.tiker,
    )

    # Создаем идентичные решения для каждой компании
    decisions = []
    for company in (company1_dto, company2_dto):
        decisions.extend(
            [
                DecisionDTO(
                    decision=DecisionEnum.SELL,
                    period=PeriodEnum.DAY,
                    tiker=company.tiker,
                ),
                DecisionDTO(
                    decision=DecisionEnum.BUY,
                    period=PeriodEnum.WEEK,
                    tiker=company.tiker,
                ),
                DecisionDTO(
                    decision=DecisionEnum.RELAX,
                    period=PeriodEnum.MONTH,
                    tiker=company.tiker,
                ),
            ]
        )

    ta_sync_service = TAService()
    messages = ta_sync_service.generate_bulk_tg_messages(
        ta_decisions=decisions,
        send_test_message=True,
    )

    assert len(messages) == 3
    assert "продавать" in messages[0]
    assert company1.tiker in messages[0]
    assert company2.tiker in messages[0]

    assert "покупать" in messages[1]
    assert company1.tiker in messages[1]
    assert company2.tiker in messages[1]

    assert "ничего" in messages[2]
    assert company1.tiker in messages[2]
    assert company2.tiker in messages[2]


@pytest.mark.anyio
async def test_generate_bulk_tg_messages_dont_send_test() -> None:
    tiker = "TST"
    decisions = [
        DecisionDTO(
            decision=DecisionEnum.BUY,
            period=PeriodEnum.DAY,
            tiker=tiker,
        ),
        DecisionDTO(
            decision=DecisionEnum.RELAX,
            period=PeriodEnum.WEEK,
            tiker=tiker,
        ),
    ]

    ta_sync_service = TAService()
    messages = ta_sync_service.generate_bulk_tg_messages(
        ta_decisions=decisions,
        send_test_message=False,
    )

    assert len(messages) == 1
    assert "покупать" in messages[0]
    assert tiker in messages[0]


@pytest.mark.anyio
async def test_fill_send_start_generate_message(
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()
    company1 = await create_test_company(dbsession, user_id=user.id)
    await create_test_company(dbsession, user_id=user.id)

    # для company1 добавляет акцию (share)
    await create_test_briefcase_share(dbsession, user_id=user.id, company=company1)

    ta_sync_service = TAService(dbsession)
    message = await ta_sync_service.fill_send_start_generate_message(
        user_id=user.id,
        period=PeriodEnum.ALL,
        send_messages=False,
        update_db=False,
        send_test_message=False,
    )

    assert message is not None
    assert len(message.companies) == 2
    assert message.companies[0].has_shares
    assert not message.companies[1].has_shares
    assert not message.send_message
    assert not message.update_db
    assert not message.send_test_message


@pytest.mark.anyio
async def test_generate_bulk_tg_messages_no_decisions() -> None:
    ta_sync_service = TAService()
    messages = ta_sync_service.generate_bulk_tg_messages(
        ta_decisions=[],
        send_test_message=False,
    )

    assert len(messages) == 0
