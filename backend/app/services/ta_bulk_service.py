import logging
from typing import Sequence

from app.db.models.company import CompanyModel
from app.schemas.ta import (
    TAFinalMessage,
    TAGenerateMessage,
    TAMessageResponse,
    TAPeriodEnum,
)
from app.worker import ta_final_task, ta_generate_task
from celery import group
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TABulkService:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def generate_ta_decisions(  # noqa:  WPS211
        self,
        user_id: int,
        period: str,
        send_messages: bool = True,
        update_db: bool = True,
        send_test_message: bool = False,
    ):
        companies = self._get_companies(user_id)

        task_group = group(
            ta_generate_task.s(
                TAGenerateMessage(
                    tiker=company.tiker,
                    user_id=user_id,
                    period=TAPeriodEnum(period),
                    update_db=False,
                    send_message=False,
                ).model_dump_json(),
            )
            for company in companies
        )
        task_chain = task_group | ta_final_task.s(
            TAFinalMessage(
                user_id=user_id,
                send_test_message=send_test_message,
                update_db=update_db,
                send_message=send_messages,
            ).model_dump_json(),
        )

        result = task_chain.apply_async()

        return TAMessageResponse(id=result.id, status=result.status)

    def _get_companies(self, user_id: int) -> Sequence[CompanyModel]:
        companies_statement = select(CompanyModel).where(
            CompanyModel.user_id == user_id,
        )
        return self.session.execute(companies_statement).scalars().fetchall()
