import logging
from collections import defaultdict
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.company import CompanyModel
from app.db.models.ta_decision import TADecisionModel
from app.schemas.ta import TADecisionDTO
from app.utils.ta.ta_sync_calculator import TACalculator
from app.utils.telegram.telegramm_sync_client import send_sync_tg_message

logger = logging.getLogger(__name__)

PERIOD_NAMES = {"M": "месяц", "D": "день", "W": "неделя"}
DECISION_NAMES = {
    "SELL": "продавать",
    "BUY": "покупать",
    "RELAX": "ничего не делать",
    "UNKNOWN": "неизвестный статус",
}


class TAService:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def update_ta_model(self, ta_decision: TADecisionDTO):
        ta_exist_statement = select(TADecisionModel).where(
            TADecisionModel.company_id == ta_decision.company.id,
            TADecisionModel.period == ta_decision.period,
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

    def generate_ta_decision(
        self,
        tiker: str,
        user_id: int,
        period: str,
    ) -> dict[str, TADecisionDTO]:
        company = self._get_company(tiker, user_id)
        ta_calculator = TACalculator()
        return ta_calculator.get_company_ta_decisions(company, period)

    def send_tg_messages(self, td_decisions: list[TADecisionDTO]):
        if td_decisions:
            for ts_decision in td_decisions:
                self._send_tg_message(ts_decision)

    def generate_bulk_tg_messages(  # noqa:  WPS210
        self,
        ta_decisions: list[TADecisionDTO],
        send_test_message: bool = False,
    ):
        if not ta_decisions:
            return []

        messages = []
        group_decisions = self._group_decisions_by_decision_and_period(ta_decisions)
        for decision_name, periods in group_decisions.items():
            if not send_test_message and decision_name not in {"BUY", "SELL"}:
                continue

            for period_name, decisions in periods.items():
                messages.append(
                    self._generate_decision_message(
                        decision_name,
                        period_name,
                        decisions,
                    ),
                )

        return messages

    def update_ta_models(self, td_decisions: list[TADecisionDTO]):
        if td_decisions:
            for ts_decision in td_decisions:
                self.update_ta_model(ts_decision)

    def _get_company(self, tiker: str, user_id: int) -> CompanyModel:
        company_statement = select(CompanyModel).where(
            CompanyModel.tiker == tiker,
            CompanyModel.user_id == user_id,
        )
        return self.session.execute(company_statement).scalars().one_or_none()

    def _group_decisions_by_decision_and_period(
        self,
        ta_decisions: List[TADecisionDTO],
    ) -> dict:
        grouped_data = defaultdict(lambda: defaultdict(list))
        for obj in ta_decisions:
            grouped_data[obj.decision][obj.period].append(obj)
        return dict(grouped_data)

    def _generate_decision_message(
        self,
        decision_name: str,
        period_name: str,
        decisions: List[TADecisionDTO],
    ):
        return self._fill_messages(
            decision_name=decision_name,
            decisions=decisions,
            period=period_name,
        )

    def _send_tg_message(self, data: TADecisionDTO):
        decision = data.decision
        period = PERIOD_NAMES[data.period]
        tiker = data.company.tiker
        name = f"[{tiker}](https://www.moex.com/ru/issue.aspx?board=TQBR&code={tiker})"
        message = f"Акции {name} ({period}) - {decision.name}"
        send_sync_tg_message(message)

    def _fill_messages(self, decision_name, decisions, period):  # noqa: WPS210
        if not decisions:
            return ""

        result = f"Акции - {DECISION_NAMES[decision_name]} ({PERIOD_NAMES[period]})!\n"
        for dec in decisions:
            tiker = dec.company.tiker
            name = (
                f"[{tiker}](https://www.moex.com/ru/issue.aspx?board=TQBR&code={tiker})"
            )
            price = round(dec.last_price, 2) if dec.last_price else None
            price_str = f" - цена: {price}" if price else ""

            # Сейчас не возвращается stop
            stop_str = ""  # f', стоп: {round(dec.stop, 2)}' if dec.stop else ''
            stoch_data_str = ""
            if dec.k and dec.d:
                ta_k = round(dec.k, 2)
                ta_d = round(dec.d, 2)
                stoch_data_str = f", k: {ta_k}, d: {ta_d}"

            result = f"{result}{name}{price_str}{stop_str}{stoch_data_str}\n"

        return result
