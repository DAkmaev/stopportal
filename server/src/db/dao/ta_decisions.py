from typing import List

from server.src.auth import get_session
from server.src.db.models.company import CompanyModel
from server.src.db.models.ta_decision import TADecisionModel
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
        decision_id,
        company: CompanyModel,
        period: str,
        decision: str,
        k: float = None,  # noqa:WPS111
        d: float = None,  # noqa:WPS111
        last_price: float = None,
    ) -> TADecisionModel:
        if not decision_id:
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

        ta_decision = await self.get_ta_decision_model(decision_id)
        ta_decision.decision = decision
        ta_decision.k = k
        ta_decision.d = d
        ta_decision.last_price = last_price

        return ta_decision
