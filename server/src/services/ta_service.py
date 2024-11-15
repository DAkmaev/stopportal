import logging
from collections import defaultdict
from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from server.src.schemas.company import CompanyDTO, CompanyStopDTO
from server.src.schemas.ta import DecisionDTO, TAStartGenerateMessage
from server.src.utils.ta.ta_calculator import TACalculator
from server.src.schemas.enums import DecisionEnum, CompanyTypeEnum, PeriodEnum
from server.src.utils.telegram.telegramm_client import send_sync_tg_message
from server.src.db.dao.companies import CompanyDAO
from server.src.db.db import get_session
from server.src.db.dao.briefcases import BriefcaseDAO
from server.src.db.dao.user import UserDAO

logger = logging.getLogger(__name__)

PERIOD_NAMES = {"M": "месяц", "D": "день", "W": "неделя"}
DECISION_NAMES = {
    "SELL": "продавать",
    "BUY": "покупать",
    "RELAX": "ничего не делать",
    "UNKNOWN": "неизвестный статус",
}


class TAService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def fill_send_start_generate_message(
        self,
        user_id: int,
        period: str,
        send_messages: bool,
        update_db: bool,
        send_test_message: bool,
    ):
        user_dao = UserDAO(session=self.session)
        company_dao = CompanyDAO(session=self.session)
        briefcase_dao = BriefcaseDAO(session=self.session)

        # TODO отправлять пачками
        LIMIT = 1000
        companies = await company_dao.get_all_companies(
            limit=LIMIT,
            user_id=user_id,
        )
        user = await user_dao.get_user(user_id)
        briefcase = await briefcase_dao.get_briefcase_model_by_user(user)
        shares = await briefcase_dao.get_all_briefcase_shares(briefcase.id)
        shared_dict = {sh.company_id: True for sh in shares}

        companies_dto = [
            CompanyDTO(
                name=company.name,
                tiker=company.tiker,
                type=CompanyTypeEnum(company.type),
                has_shares=shared_dict.get(company.id, False),
                stops=[
                    CompanyStopDTO(
                        period=stop.period,
                        value=stop.value,
                    )
                    for stop in company.stops
                ],

            )
            for company in companies
        ]

        message = TAStartGenerateMessage(
            user_id=user_id,
            period=PeriodEnum(period),
            companies=companies_dto,
            update_db=update_db,
            send_message=send_messages,
            send_test_message=send_test_message,
        )
        logging.debug(f"********* TAStartGenerateMessage: {message}")
        return message

    def generate_ta_decision(
        self,
        company: CompanyDTO,
        period: str,
    ) -> dict[str, DecisionDTO]:
        ta_calculator = TACalculator()
        decisions = ta_calculator.get_company_ta_decisions(company, period)

        for key in decisions:
            if not company.has_shares and decisions[key].decision == DecisionEnum.SELL:
                logger.debug(f"Заменяем решение SELL на RELAX, так как нет акций в портфеле")
                decisions[key].decision = DecisionEnum.RELAX

        return decisions

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
                # TODO Надо эту логику перенести выше
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
