import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.dao.companies import CompanyDAO
from backend.app.db.dao.ta_decisions import TADecisionDAO
from backend.tests.utils.common import create_test_user, create_test_company


@pytest.mark.anyio
async def test_get_ta_decision(
    dbsession: AsyncSession,
) -> None:
    decision_dao = TADecisionDAO(dbsession)

    # Create a test companies
    company1 = await create_test_company(dbsession)
    company2 = await create_test_company(dbsession)

    # Create a StochDecisionModel
    ta_decision1 = await decision_dao.update_or_create_ta_decision_model(
        company1, "D", "BUY", 0.5, 0.3, 100.0
    )
    ta_decision2 = await decision_dao.update_or_create_ta_decision_model(
        company2, "W", "SELL", 1.0, 1.2, 200.0
    )

    ############## By company_id
    decisions_by_company = await decision_dao.get_ta_decision_models_by_company_id(
        company1.id
    )
    assert len(decisions_by_company) == 1

    decision_by_company = decisions_by_company[0]
    assert decision_by_company.k == 0.5
    assert decision_by_company.d == 0.3
    assert decision_by_company.last_price == 100.0

    ############## All decisions
    decisions = await decision_dao.get_ta_decision_models()

    assert len(decisions) == 2

    decision1 = decisions[0]
    assert decision1.k == 0.5
    assert decision1.d == 0.3
    assert decision1.last_price == 100.0

    decision2 = decisions[1]
    assert decision2.k == 1.0
    assert decision2.d == 1.2
    assert decision2.last_price == 200.0

    ############## By ID
    decision = await decision_dao.get_ta_decision_model(ta_decision2.id)
    assert decision.k == 1.0
    assert decision.d == 1.2
    assert decision.last_price == 200.0

    ############## By period
    dec_by_period = await decision_dao.get_ta_decision_model_by_company_period(
        company_id=company1.id, period="D"
    )
    assert dec_by_period is not None
    assert dec_by_period.k == 0.5
    assert dec_by_period.d == 0.3
    assert dec_by_period.last_price == 100.0

    dec_by_period_none = await decision_dao.get_ta_decision_model_by_company_period(
        company_id=company1.id, period="W"
    )
    assert dec_by_period_none is None


@pytest.mark.anyio
async def test_update_stoch_decisions(
    dbsession: AsyncSession,
) -> None:
    decision_dao = TADecisionDAO(dbsession)
    period = "W"

    # Create a test company
    company = await create_test_company(dbsession)

    # Create a StochDecisionModel
    await decision_dao.update_or_create_ta_decision_model(
        company, period, "BUY", 0.5, 0.3, 100.0
    )

    # Modify the StochDecisionModel
    updated_decision = "SELL"
    ta_decision = await decision_dao.update_or_create_ta_decision_model(
        company, period, updated_decision, 0.4, 0.6, 110.0
    )

    assert ta_decision.decision == updated_decision
    assert ta_decision.k == 0.4
    assert ta_decision.d == 0.6
    assert ta_decision.last_price == 110.0
