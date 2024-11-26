from typing import List

from backend.app.db.db import get_session
from backend.app.db.models.company import CompanyModel
from backend.app.db.models.ta_decision import TADecisionModel
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TADecisionDAO:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_ta_decision_models(self) -> List[TADecisionModel]:
        query = select(TADecisionModel)
        # if period:
        #     query = query.where(StochDecisionModel.period == period)

        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

    async def get_ta_decision_model(self, decision_id: int) -> TADecisionModel:
        ta_decision = await self.session.get(TADecisionModel, decision_id)

        if not ta_decision:
            raise HTTPException(status_code=404, detail="Запись о TA не найдена")

        return ta_decision

    async def get_ta_decision_models_by_company_id(
        self,
        company_id: int,
    ) -> List[TADecisionModel]:
        ta_decisions = await self.session.execute(
            select(TADecisionModel).where(TADecisionModel.company_id == company_id),
        )

        return ta_decisions.scalars().fetchall()

    async def get_ta_decision_model_by_company_period(
        self,
        company_id: int,
        period: str,
    ) -> TADecisionModel:
        ta_decisions = await self.session.execute(
            select(TADecisionModel).where(
                TADecisionModel.company_id == company_id,
                TADecisionModel.period == period,
            ),
        )

        return ta_decisions.scalars().one_or_none()

    async def update_or_create_ta_decision_model(  # noqa:WPS211
        self,
        company: CompanyModel,
        period: str,
        decision: str,
        k: float = None,  # noqa:WPS111
        d: float = None,  # noqa:WPS111
        last_price: float = None,
    ) -> TADecisionModel:
        exist_decision = await self.get_ta_decision_model_by_company_period(
            company_id=company.id, period=period
        )
        if not exist_decision:
            ta_decision = TADecisionModel(
                period=period,
                decision=decision,
                k=k,
                d=d,
                last_price=last_price,
                company_id=company.id,
            )
            self.session.add(ta_decision)

            return ta_decision

        exist_decision.decision = decision
        exist_decision.k = k
        exist_decision.d = d
        exist_decision.last_price = last_price

        return exist_decision
