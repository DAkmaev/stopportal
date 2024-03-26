import logging
from app.db.dao.companies import CompanyDAO
from app.web.api.ta.scheme import TADecisionDTO
from fastapi import Depends

logger = logging.getLogger(__name__)

PERIOD_NAMES = {"M": "месяц", "D": "день", "W": "неделя"}


class TAGenerateService:
    def __init__(
        self,
        company_dao: CompanyDAO = Depends(),
    ):
        # self.ta_calculator = TACalculator()
        self.company_dao = company_dao

    async def generate_ta_decision(  # noqa: WPS210
        self,
        tiker: str,
        user_id: int,
        period: str = "All",
    ) -> TADecisionDTO:
        company = await self.company_dao.get_company_model_by_tiker(
            tiker=tiker,
            user_id=user_id,
        )
        #decision_model = self.ta_calculator.get_company_ta_decisions(company, period)
        return TADecisionDTO(

        )
