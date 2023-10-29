import asyncio

from fastapi import Depends

from backend.db.dao.companies import CompanyDAO
from backend.db.dao.cron_job import CronJobRunDao
from backend.utils.stoch.stoch_calculator import StochCalculator
from backend.utils.telegram.telegramm_client import send_tg_message
from backend.web.api.stoch.scheme import StochDecisionEnum, StochDecisionModel


class StochService:
    def __init__(self, company_dao: CompanyDAO = Depends(),
                 cron_dao: CronJobRunDao = Depends()):
        self.stoch_calculator = StochCalculator()
        self.company_dao = company_dao
        self.cron_dao = cron_dao

    async def _fetch_stoch_decision(self, st, period):
        return await self.stoch_calculator.get_stoch_decision(
            st.tiker,
            st.type,
            period,
            st.stops[0].value if st.stops else None
        )

    def _fill_message(self, decision, companies, period):
        if len(companies) == 0:
            return ''

        period_str = 'месяц' if period == 'M' else 'день' if period == 'D' else 'неделя'

        result = f'Акции {decision} ({period_str})!\n'
        for dec in companies:
            name = f'[{dec.tiker}](https://www.moex.com/ru/issue.aspx?board=TQBR&code={dec.tiker})'
            price_str = f' - цена: {round(dec.last_price, 2)}'
            stop_str = f', стоп: {round(dec.stop, 2)}' if dec.stop else ''
            stoch_data_str = ''
            if dec.k and dec.d:
                k = round(dec.k, 2)
                d = round(dec.d, 2)
                stoch_data_str = f', k: {k}, d: {d}'

            result += f'{name}{price_str}{stop_str}{stoch_data_str}\n'

        return result

    async def get_stochs(self, period: str = 'W', is_cron: bool = False,
                         send_messages: bool = True, send_test: bool = False):
        companies = await self.company_dao.get_all_companies()
        des_futures = [self._fetch_stoch_decision(st, period) for st in companies]
        decisions = await asyncio.gather(*des_futures)

        companies_to_buy = list(
            filter(lambda d: d.decision == StochDecisionEnum.BUY, decisions))
        companies_to_sell = list(
            filter(lambda d: d.decision == StochDecisionEnum.SELL, decisions))
        companies_to_relax = list(
            filter(lambda d: d.decision == StochDecisionEnum.RELAX, decisions))

        if send_messages:
            send_tasks = [
                send_tg_message(
                    self._fill_message("продавать", companies_to_sell, period)),
                send_tg_message(
                    self._fill_message("покупать", companies_to_buy, period))
            ]
            if send_test:
                send_tasks.append(
                    send_tg_message(
                        self._fill_message("тест", companies_to_relax, period)))

            await asyncio.gather(*send_tasks)

        return decisions

    async def get_stoch(
        self,
        tiker: str, period: str = 'W', send_messages: bool = False
    ) -> StochDecisionModel:
        company = await self.company_dao.get_company_model_by_tiker(tiker=tiker)
        stops_same_period = list(filter(lambda s: s.period == period, company.stops))
        stop_value = stops_same_period[0].value if stops_same_period else None

        decision_model = await self.stoch_calculator.get_stoch_decision(
            tiker, company.type, period, stop_value
        )

        if send_messages:
            message = f""" Акции {tiker}
                Вывод: {decision_model.decision.name}
                """
            await send_tg_message(message)

        return decision_model
