import asyncio

from fastapi import Depends

from backend.db.dao.briefcases import BriefcaseDAO
from backend.db.dao.companies import CompanyDAO
from backend.db.dao.cron_job import CronJobRunDao
from backend.db.dao.stoch_decisions import StochDecisionDAO
from backend.db.models.company import CompanyModel
from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.utils.telegram.telegramm_client import send_tg_message
from backend.web.api.stoch.scheme import StochDecisionDTO, StochDecisionEnum

PERIOD_NAMES = {'M': 'месяц', 'D': 'день', 'W': 'неделя'}


class StochService:
    def __init__(
        self,
        company_dao: CompanyDAO = Depends(),
        cron_dao: CronJobRunDao = Depends(),
        stoch_dao: StochDecisionDAO = Depends(),
        briefcase_dao: BriefcaseDAO = Depends()
    ):
        self.stoch_calculator = StochCalculator()
        self.company_dao = company_dao
        self.stoch_dao = stoch_dao
        self.cron_dao = cron_dao
        self.briefcase_dao = briefcase_dao

    async def _update_stoch(self, company: CompanyModel, period: str, decision: StochDecisionDTO):
        exist_stoch_decision = await self.stoch_dao.get_stoch_decision_model_by_company_period(
            company_id=company.id, period=period)
        stoch_decision = await self.stoch_dao.update_or_create_stoch_decision_model(
            id=exist_stoch_decision.id if exist_stoch_decision else None,
            company=company,
            period=period,
            decision=decision.decision.name,
            k=decision.k,
            d=decision.d,
            last_price=decision.last_price
        )
        return stoch_decision

    async def _fetch_stoch_decisions(self, st, period):
        return await self.stoch_calculator.get_stoch_decisions(st, period)

    def _fill_messages(self, decision, companies, period):
        if len(companies) == 0:
            return ''

        result = f'Акции {decision} ({PERIOD_NAMES[period]})!\n'
        for dec in companies:
            name = f'[{dec.company.tiker}](https://www.moex.com/ru/issue.aspx?board=TQBR&code={dec.company.tiker})'
            price_str = f' - цена: {round(dec.last_price, 2)}'

            # Сейчас не возвращается stop
            stop_str = '' # f', стоп: {round(dec.stop, 2)}' if dec.stop else ''
            stoch_data_str = ''
            if dec.k and dec.d:
                k = round(dec.k, 2)
                d = round(dec.d, 2)
                stoch_data_str = f', k: {k}, d: {d}'

            result += f'{name}{price_str}{stop_str}{stoch_data_str}\n'

        return result

    async def generate_stoch_decisions(self, briefcase_id: int, period: str = 'ALL', is_cron: bool = False,
                         send_messages: bool = True, send_test: bool = False):
        companies = await self.company_dao.get_all_companies()
        # companies = companies[:200:]
        result = dict()

        briefcase_items = await self.briefcase_dao.get_briefcase_items_by_briefcase(briefcase_id)
        briefcase_dict = {b.company.id: b for b in briefcase_items}

        # Разбиваем список компаний на группы по 150 итераций
        for i in range(0, len(companies), 150):
            batch_companies = companies[i:i + 150]

            des_futures = [self._fetch_stoch_decisions(st, period) for st in batch_companies]
            decisions = await asyncio.gather(*des_futures)

            for per_desisions in decisions:
                for p in per_desisions:
                    decision = per_desisions[p]

                    # для SELL проверяем, есть ли акции в портфеле, если нет, то Relax
                    if decision.decision == StochDecisionEnum.SELL and decision.company.id not in briefcase_dict:
                        decision.decision = StochDecisionEnum.RELAX

                    await self._update_stoch(decision.company, p, decision)
                    result.setdefault(p, {}).setdefault(decision.decision.name, []).append(decision)

        if send_messages:
            for per in result.keys():
                send_tasks = [
                    send_tg_message(
                        self._fill_messages("продавать", result[per].setdefault('SELL', []), per)),
                    send_tg_message(
                        self._fill_messages("покупать", result[per].setdefault('BUY', []), per))
                ]
                if send_test:
                    send_tasks.append(
                        send_tg_message(
                            self._fill_messages("тест", result[per].setdefault('RELAX', []), per)))

                await asyncio.gather(*send_tasks)

        return result

    async def generate_stoch_decision(
        self,
        tiker: str, period: str = 'All', send_messages: bool = False
    ) -> StochDecisionDTO:
        company = await self.company_dao.get_company_model_by_tiker(tiker=tiker)
        decision_model = await self.stoch_calculator.get_stoch_decisions(
            company, period
        )

        for per in decision_model.keys():
            await self._update_stoch(company, per, decision_model[per])
            if send_messages:
                name = f'[{tiker}](https://www.moex.com/ru/issue.aspx?board=TQBR&code={tiker})'
                message = f'Акции {name} ({PERIOD_NAMES[per]}) - {decision_model[per].decision.name}'
                await send_tg_message(message)

        return decision_model
