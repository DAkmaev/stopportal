from sqlalchemy import select
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.db.models.company import CompanyModel
from app.db.models.ta_decision import TADecisionModel


class TADecisionDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_ta_decision_models(self) -> List[TADecisionModel]:
        """
        Get ta_decision models.
        """
        query = select(TADecisionModel)
        # if period:
        #     query = query.where(StochDecisionModel.period == period)

        rows = await self.session.execute(query)
        sc_rows = list(rows.scalars().fetchall())
        return sc_rows

    async def get_ta_decision_model(self, id: int) -> TADecisionModel:
        """
        Get ta_decision model.

        """
        ta_decision = await self.session.get(TADecisionModel, id)

        if not ta_decision:
            raise HTTPException(status_code=404, detail="Запись о TA не найдена")

        return ta_decision

    async def get_ta_decision_models_by_company_id(
        self, company_id: int
    ) -> List[TADecisionModel]:
        """
        Get ta_decision models by company.

        """

        ta_decisions = await self.session.execute(
            select(TADecisionModel).where(TADecisionModel.company_id == company_id)
        )

        return ta_decisions.scalars().fetchall()

    async def get_ta_decision_model_by_company_period(
        self, company_id: int, period: str
    ) -> TADecisionModel:
        """
        Get ta_decision models by company and period.

        """

        ta_decisions = await self.session.execute(
            select(TADecisionModel).where(
                TADecisionModel.company_id == company_id,
                TADecisionModel.period == period,
            )
        )

        return ta_decisions.scalars().one_or_none()

    async def update_or_create_ta_decision_model(
        self,
        id,
        company: CompanyModel,
        period: str,
        decision: str,
        k: float = None,
        d: float = None,
        last_price: float = None,
    ) -> TADecisionModel:
        """
        Update orcompany model in the session.
        """

        if not id:
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

        ta_decision = await self.get_ta_decision_model(id)
        ta_decision.decision = decision
        ta_decision.k = k
        ta_decision.d = d
        ta_decision.last_price = last_price

        return ta_decision
