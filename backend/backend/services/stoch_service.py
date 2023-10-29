import asyncio
import concurrent
import time

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

    async def _fetch_stoch_decisions(self, st, period):
        return await self.stoch_calculator.get_stoch_decisions(
            st.tiker,
            st.type,
            period,
            st.stops
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
        des_futures = [self._fetch_stoch_decisions(st, period) for st in companies]
        decisions = await asyncio.gather(*des_futures)

        result = dict()
        for per_des in decisions:
            for p in per_des:
                decision = per_des[p].decision
                result.setdefault(p, {}).setdefault(decision.name, []).append(per_des[p])

        if send_messages:
            for per in result.keys():
                send_tasks = [
                    send_tg_message(
                        self._fill_message("продавать", result[per].setdefault('SELL', []), per)),
                    send_tg_message(
                        self._fill_message("покупать", result[per].setdefault('BUY', []), per))
                ]
                if send_test:
                    send_tasks.append(
                        send_tg_message(
                            self._fill_message("тест", result[per].setdefault('RELUX', []), per)))

                await asyncio.gather(*send_tasks)

        return result

    async def get_stoch(
        self,
        tiker: str, period: str = 'All', send_messages: bool = False
    ) -> StochDecisionModel:
        company = await self.company_dao.get_company_model_by_tiker(tiker=tiker)
        decision_model = await self.stoch_calculator.get_stoch_decisions(
            tiker, company.type, period, company.stops
        )

        if send_messages:
            message = f""" Акции {tiker}
                Вывод: {decision_model[period].decision.name}
                """
            await send_tg_message(message)

        return decision_model


    # def sync_function(self, tiker:str):
    #     time.sleep(1)
    #     return StochDecisionModel(
    #         decision=StochDecisionEnum.RELAX,
    #         tiker=tiker
    #     )
    # async def _get_decision_test(self, tiker, semaphore):
    #     async with semaphore:
    #         with concurrent.futures.ThreadPoolExecutor() as executor:
    #             result = await asyncio.get_event_loop().run_in_executor(executor, lambda: self.sync_function(tiker))
    #             return result
    #
    #
    # async def get_stochs_test(self) -> StochDecisionModel:
    #     print(f"\nstarted at {time.strftime('%X')}")
    #
    #     semaphore = asyncio.Semaphore(2)  # Ограничение на количество одновременных потоков
    #     tasks = [self._get_decision_test(f'{_}', semaphore) for _ in range(10)]
    #     results = await asyncio.gather(*tasks)
    #
    #     print(f"finished at {time.strftime('%X')}")
    #     return results

