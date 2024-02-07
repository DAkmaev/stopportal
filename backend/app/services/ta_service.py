import asyncio
import os

import pandas as pd
from fastapi import Depends

from app.db.dao.briefcases import BriefcaseDAO
from app.db.dao.companies import CompanyDAO
from app.db.dao.cron_job import CronJobRunDao
from app.db.dao.ta_decisions import TADecisionDAO
from app.db.models.company import CompanyModel
from app.utils.ta.ta_calculator import TACalculator, TADecision
from app.utils.telegram.telegramm_client import send_tg_message
from app.web.api.ta.scheme import TADecisionDTO, TADecisionEnum

PERIOD_NAMES = {'M': 'месяц', 'D': 'день', 'W': 'неделя'}


class TAService:
    def __init__(
        self,
        company_dao: CompanyDAO = Depends(),
        cron_dao: CronJobRunDao = Depends(),
        stoch_dao: TADecisionDAO = Depends(),
        briefcase_dao: BriefcaseDAO = Depends()
    ):
        self.ta_calculator = TACalculator()
        self.company_dao = company_dao
        self.stoch_dao = stoch_dao
        self.cron_dao = cron_dao
        self.briefcase_dao = briefcase_dao

    async def _update_stoch(self, company: CompanyModel, period: str, decision: TADecisionDTO):
        exist_ta_decision = await self.stoch_dao.get_ta_decision_model_by_company_period(
            company_id=company.id, period=period)
        ta_decision = await self.stoch_dao.update_or_create_ta_decision_model(
            id=exist_ta_decision.id if exist_ta_decision else None,
            company=company,
            period=period,
            decision=decision.decision.name,
            k=decision.k,
            d=decision.d
            #last_price=decision.last_price
        )
        return ta_decision

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

    async def generate_ta_decisions(self, briefcase_id: int, period: str = 'ALL', is_cron: bool = False,
                         send_messages: bool = True, send_test: bool = False):
        companies = await self.company_dao.get_all_companies()
        # companies = companies[:200:]
        result = dict()

        briefcase_items = await self.briefcase_dao.get_briefcase_items_by_briefcase(briefcase_id)
        briefcase_dict = {b.company.id: b for b in briefcase_items}

        decisions = await self.ta_calculator.get_companies_ta_decisions(companies, period)

        for per_desisions in decisions:
            for p in per_desisions:
                decision = per_desisions[p]

                # для SELL проверяем, есть ли акции в портфеле, если нет, то Relax
                # todo раскоментировать, когда заполнится портфель
                # if decision.decision == StochDecisionEnum.SELL and decision.company.id not in briefcase_dict:
                #     decision.decision = StochDecisionEnum.RELAX

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

    async def generate_ta_decision(
        self,
        tiker: str, period: str = 'All', send_messages: bool = False
    ) -> TADecisionDTO:
        company = await self.company_dao.get_company_model_by_tiker(tiker=tiker)
        decision_model = self.ta_calculator.get_company_ta_decisions(
            company, period
        )

        for per in decision_model.keys():
            await self._update_stoch(company, per, decision_model[per])
            if send_messages:
                name = f'[{tiker}](https://www.moex.com/ru/issue.aspx?board=TQBR&code={tiker})'
                message = f'Акции {name} ({PERIOD_NAMES[per]}) - {decision_model[per].decision.name}'
                await send_tg_message(message)

        return decision_model

    async def history_stochs(self, tiker: str) -> dict:
        company = await self.company_dao.get_company_model_by_tiker(tiker=tiker)
        df = self.ta_calculator.get_history_data(company, 3650, False)
        low_data = False

        bottom_border: float = 25
        # top_border: float = 80

        result_df = pd.DataFrame(columns=['Buy', 'Buy_M', 'Buy_ADX', 'Sell', 'last_price', 'k', 'd', 'k_M', 'd_M'])

        while not low_data:
            if df.size == 0:
                low_data = True
                continue

            stoch_D = self.ta_calculator.generate_ta_indicators(df, "D")
            stoch_M = self.ta_calculator.generate_ta_indicators(df, "M")

            if stoch_D.size == 0 or stoch_M.size == 0:
                low_data = True
                continue

            last_row_D = stoch_D.iloc[-1]
            last_row_M = stoch_M.iloc[-1]

            date = str(last_row_D.name.date())

            has_decision = False
            if last_row_D.d < last_row_D.k < bottom_border:
                has_decision = True
                result_df.loc[date, 'Buy'] = 'X'

            if last_row_D.d < last_row_D.k < bottom_border and last_row_M.d < last_row_M.k:
                has_decision = True
                result_df.loc[date, 'Buy_M'] = 'X'

            if last_row_D.k < last_row_D.d:
                has_decision = True
                result_df.loc[date, 'Sell'] = 'X'

            if last_row_M.k > last_row_M.d and last_row_D.dmp > last_row_D.dmn:
                has_decision = True
                result_df.loc[date, 'Buy_ADX'] = 'X'

            if has_decision:
                last_price = df.iloc[-1]['CLOSE']
                result_df.loc[date, 'last_price'] = round(last_price, 2)
                result_df.loc[date, 'k'] = str(round(last_row_D.k, 4))
                result_df.loc[date, 'd'] = str(round(last_row_D.d, 4))
                result_df.loc[date, 'k_M'] = str(round(last_row_M.k, 4))
                result_df.loc[date, 'd_M'] = str(round(last_row_M.d, 4))
                result_df.loc[date, 'adx'] = str(round(last_row_D.adx, 4))
                result_df.loc[date, 'dmp'] = str(round(last_row_D.dmp, 4))
                result_df.loc[date, 'dmn'] = str(round(last_row_D.dmn, 4))

            df = df[:-1]

        # with pd.ExcelWriter('history.xlsx', mode='a') as writer:
        #     result_df.to_excel(writer, sheet_name=tiker)

        # result_df.sort_index(ascending=False, inplace=True)
        file_name = f'history_{tiker}.csv'
        current_directory = os.getcwd()
        result_df.to_csv(file_name, ';')

        return {'status': 'SUCCESS', 'file_name': file_name, 'path': current_directory}

