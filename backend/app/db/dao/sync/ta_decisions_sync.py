from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.ta_decision import TADecisionModel
from app.schemas.ta import TADecisionDTO


class TADecisionSyncDAO:
    def __init__(self, session: Session):
        self.session = session

    def update_ta_model(self, ta_decision: TADecisionDTO):
        ta_exist_statement = select(TADecisionModel).where(
            TADecisionModel.company_id == ta_decision.company.id,
            TADecisionModel.period == ta_decision.period,
        )
        exist_ta = self.session.execute(ta_exist_statement).scalars().one_or_none()

        if exist_ta:
            exist_ta.decision = ta_decision.decision
            exist_ta.k = ta_decision.k
            exist_ta.d = ta_decision.d
            exist_ta.last_price = ta_decision.last_price
        else:
            new_ta = TADecisionModel(
                company_id=ta_decision.company.id,
                period=ta_decision.period,
                decision=ta_decision.decision,
                k=ta_decision.k,
                d=ta_decision.d,
                last_price=ta_decision.last_price,
            )
            self.session.add(new_ta)

    def update_ta_models(self, td_decisions: list[TADecisionDTO]):
        if td_decisions:
            for ts_decision in td_decisions:
                self.update_ta_model(ts_decision)
