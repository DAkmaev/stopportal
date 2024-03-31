import logging
from typing import List, Sequence

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.models.company import CompanyModel
from app.db.models.ta_decision import TADecisionModel
from app.schemas.Ta import TADecisionDTO
from app.utils.ta.ta_sync_calculator import TACalculator, TADecision
from app.utils.telegram.telegramm_sync_client import send_sync_tg_message

# from app.web.api.ta.scheme import TADecisionDTO

logger = logging.getLogger(__name__)

PERIOD_NAMES = {"M": "месяц", "D": "день", "W": "неделя"}


class TAService:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def _get_company(self, tiker: str, user_id: int) -> CompanyModel:
        company_statement = (
            select(CompanyModel)
            .where(CompanyModel.tiker == tiker, CompanyModel.user_id == user_id)
        )
        return self.session.execute(company_statement).scalars().one_or_none()

    def _update_ta_model(self, ta_decision: TADecisionDTO):
        ta_exist_statement = (
            select(TADecisionModel)
            .where(
                TADecisionModel.company_id == ta_decision.company.id,
                TADecisionModel.period == ta_decision.period,
                )
        )
        exist_ta = self.session.execute(ta_exist_statement).scalars().one_or_none()

        if exist_ta:
            exist_ta.decision = ta_decision.decision
            exist_ta.k = ta_decision.k
            exist_ta.d = ta_decision.d
            exist_ta.last_price = ta_decision.last_price
        else:
            new_ta = TADecisionModel(
                company_id=ta_decision.company.id,
                period=ta_decision.period,
                decision=ta_decision.decision,
                k=ta_decision.k,
                d=ta_decision.d,
                last_price=ta_decision.last_price,
            )
            self.session.add(new_ta)

    def generate_ta_decision(self, tiker: str, user_id: int, period: str, send_message: bool):
        company = self._get_company(tiker, user_id)
        ta_calculator = TACalculator()
        decisions = ta_calculator.get_company_ta_decisions(company, period)

        self.update_ta_models(decisions)
        if send_message:
            self.send_tg_messages(decisions)

        return decisions

    def send_tg_messages(self, td_decisions: dict[str, TADecisionDTO]):
        if len(td_decisions.keys()) > 0:
            for per in td_decisions.keys():
                self._send_tg_message(td_decisions[per])

    def update_ta_models(self, td_decisions: dict[str, TADecisionDTO]):
        if len(td_decisions.keys()) > 0:
            for per in td_decisions.keys():
                self._update_ta_model(td_decisions[per])

    def _send_tg_message(self, data: TADecisionDTO):
        decision = data.decision
        period = PERIOD_NAMES[data.period]
        name = f"[{data.company.tiker}](https://www.moex.com/ru/issue.aspx?board=TQBR&code={data.company.tiker})"
        message = f"Акции {name} ({period}) - {decision.name}"
        send_sync_tg_message(message)
