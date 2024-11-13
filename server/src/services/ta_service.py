import logging
from collections import defaultdict
from typing import List

from server.src.schemas.company import CompanyDTO
from server.src.schemas.ta import DecisionDTO
from server.src.utils.ta.ta_calculator import TACalculator

logger = logging.getLogger(__name__)

PERIOD_NAMES = {"M": "месяц", "D": "день", "W": "неделя"}
DECISION_NAMES = {
    "SELL": "продавать",
    "BUY": "покупать",
    "RELAX": "ничего не делать",
    "UNKNOWN": "неизвестный статус",
}


class TAService:
    def generate_ta_decision(
        self,
        company: CompanyDTO,
        period: str,
    ) -> dict[str, DecisionDTO]:
        ta_calculator = TACalculator()
        return ta_calculator.get_company_ta_decisions(company, period)

    def send_tg_messages(self, td_decisions: list[DecisionDTO]):
        if td_decisions:
            for ts_decision in td_decisions:
                self._send_tg_message(ts_decision)

    def generate_bulk_tg_messages(  # noqa:  WPS210
        self,
        ta_decisions: list[DecisionDTO],
        send_test_message: bool = False,
    ):
        if not ta_decisions:
            return []

        messages = []
        group_decisions = self._group_decisions_by_decision_and_period(ta_decisions)
        for decision_name, periods in group_decisions.items():
            if not send_test_message and decision_name not in {  # noqa: WPS337
                DecisionEnum.BUY,
                DecisionEnum.SELL,
            }:
                continue

            for period_name, decisions in periods.items():
                # decisions_filtered = [
                #     dec
                #     for dec in decisions
                #     if dec.company.has_shares or decision_name != DecisionEnum.SELL
                # ]
                # if decisions_filtered:
                if decisions:
                    messages.append(
                        self._generate_decision_message(
                            decision_name,
                            period_name,
                            decisions,
                        ),
                    )

        return messages

    def _group_decisions_by_decision_and_period(
        self,
        ta_decisions: List[DecisionDTO],
    ) -> dict:
        grouped_data = defaultdict(lambda: defaultdict(list))
        for obj in ta_decisions:
            grouped_data[obj.decision][obj.period].append(obj)
        return dict(grouped_data)

    def _generate_decision_message(
        self,
        decision_name: str,
        period_name: str,
        decisions: List[DecisionDTO],
    ):
        return self._fill_messages(
            decision_name=decision_name,
            decisions=decisions,
            period=period_name,
        )

    def _send_tg_message(self, data: DecisionDTO):
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
            name = f"[{dec.tiker}](https://www.moex.com/ru/issue.aspx?board=TQBR&code={dec.tiker})"
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
