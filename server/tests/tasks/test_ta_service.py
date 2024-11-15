from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from server.src.services.ta_service import TAService
from server.src.schemas.company import CompanyDTO
from server.src.schemas.enums import DecisionEnum, PeriodEnum
from server.src.schemas.ta import DecisionDTO
from server.tests.utils.common import create_test_company, create_test_briefcase, create_test_briefcase_share


@pytest.mark.anyio
async def test_generate_bulk_tg_messages(
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()
    company1 = await create_test_company(dbsession, user_id=user.id)
    company2 = await create_test_company(dbsession, user_id=user.id)
    briefcase = await create_test_briefcase(dbsession, user_id=user.id)

    # создаем акцию в портфеле для company
    share = await create_test_briefcase_share(
        dbsession,
        user_id=user.id,
        company=company1,
        briefcase=briefcase,
    )

    company1_dto = CompanyDTO(
        id=company1.id, name=company1.name, tiker=company1.tiker
    )
    company2_dto = CompanyDTO(
        id=company2.id, name=company2.name, tiker=company2.tiker
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
        ta_decisions=decisions, send_test_message=True, shares=[share]
    )

    assert len(messages) == 3
    assert "продавать" in messages[0]
    assert company1.tiker in messages[0]
    assert company2.tiker not in messages[0]

    assert "покупать" in messages[1]
    assert company1.tiker in messages[1]
    assert company2.tiker in messages[1]

    assert "ничего" in messages[2]
    assert company1.tiker in messages[2]
    assert company2.tiker in messages[2]


@pytest.mark.anyio
async def test_generate_bulk_tg_messages_dont_send_test(
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()
    company = await create_test_company(dbsession, user_id=user.id)
    decisions = [
        DecisionDTO(
            decision=DecisionEnum.BUY,
            period=PeriodEnum.DAY,
            tiker=company.tiker,
        ),
        DecisionDTO(
            decision=DecisionEnum.RELAX,
            period=PeriodEnum.WEEK,
            tiker=company.tiker,
        ),
    ]

    ta_sync_service = TAService()
    messages = ta_sync_service.generate_bulk_tg_messages(
        ta_decisions=decisions,
        send_test_message=False,
    )

    assert len(messages) == 1
    assert "покупать" in messages[0]
    assert company.tiker in messages[0]


@pytest.mark.anyio
async def test_generate_bulk_tg_messages_filtered(
    dbsession: AsyncSession,
    user_token_headers: dict[str, Any],
) -> None:
    user, headers = user_token_headers.values()
    company = await create_test_company(dbsession, user_id=user.id)
    decisions = [
        DecisionDTO(
            tiker=company.tiker,
            decision=DecisionEnum.SELL,
            period=PeriodEnum.DAY,
        ),
    ]

    ta_sync_service = TAService(dbsession)
    # хоть decisions есть, но этих акций нет в портфеле, не должно быть сообщений
    messages = ta_sync_service.generate_bulk_tg_messages(
        ta_decisions=decisions,
    )

    assert len(messages) == 0
    #assert 'Акции - продавать (день)' in messages[0]


@pytest.mark.anyio
async def test_generate_bulk_tg_messages_no_decisions() -> None:
    ta_sync_service = TAService()
    messages = ta_sync_service.generate_bulk_tg_messages(
        ta_decisions=[],
        send_test_message=False,
    )

    assert len(messages) == 0
