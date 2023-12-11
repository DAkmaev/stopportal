from sqlalchemy import select
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dependencies import get_db_session
from backend.db.models.company import CompanyModel
from backend.db.models.stoch_decision import StochDecisionModel


class StochDecisionDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_stoch_decision_models(self) -> List[StochDecisionModel]:
        """
        Get stoch_decision models.
        """
        query = select(StochDecisionModel)
        # if period:
        #     query = query.where(StochDecisionModel.period == period)

        rows = await self.session.execute(query)
        sc_rows = list(rows.scalars().fetchall())
        return sc_rows

    async def get_stoch_decision_model(self, id: int) -> StochDecisionModel:
        """
        Get stoch_decision model.

        """
        stoch_decision = await self.session.get(StochDecisionModel, id)

        if not stoch_decision:
            raise HTTPException(status_code=404, detail="Запись о stoch не найдена")

        return stoch_decision

    async def get_stoch_decision_models_by_company_id(self, company_id: int) -> List[StochDecisionModel]:
        """
        Get stoch_decision models by company.

        """

        stoch_decisions = await self.session.execute(
            select(StochDecisionModel).where(StochDecisionModel.company_id == company_id)
        )

        return stoch_decisions.scalars().fetchall()

    async def get_stoch_decision_model_by_company_period(self, company_id: int, period: str) -> StochDecisionModel:
        """
        Get stoch_decision models by company and period.

        """

        stoch_decisions = await self.session.execute(
            select(StochDecisionModel).where(StochDecisionModel.company_id == company_id, StochDecisionModel.period == period)
        )

        return stoch_decisions.scalars().one_or_none()

    async def update_or_create_stoch_decision_model(
        self, id,
        company: CompanyModel,
        period: str,
        decision: str,
        k: float = None,
        d: float = None,
        last_price: float = None
    ) -> StochDecisionModel:
        """
        Update orcompany model in the session.
        """

        if not id:
            stoch_decision = StochDecisionModel(
                period=period,
                decision=decision,
                k=k,
                d=d,
                last_price=last_price,
                company_id=company.id
            )
            self.session.add(stoch_decision)

            return stoch_decision

        stoch_decision = await self.get_stoch_decision_model(id)
        stoch_decision.decision = decision
        stoch_decision.k = k
        stoch_decision.d = d
        stoch_decision.last_price = last_price

        return stoch_decision
