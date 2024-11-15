import logging

from server.src.schemas.ta import (
    TAStartGenerateMessage,
    PeriodEnum,
    TAMessageResponse,
    TAMessageStatus,
)
from fastapi import APIRouter, Depends

from server.src.auth import CurrentUser
from server.src.worker.tasks import start_generate_task
from server.src.db.dao.companies import CompanyDAO
from server.src.schemas.company import CompanyDTO,  CompanyStopDTO
from server.src.schemas.enums import CompanyTypeEnum

router = APIRouter()


@router.post("/")
async def run_generate_ts_decisions(
    current_user: CurrentUser,
    period: str = "All",
    send_messages: bool = False,
    update_db: bool = False,
    send_test_message: bool = False,
    company_dao: CompanyDAO = Depends(),
) -> TAMessageResponse:
    # TODO отправлять пачками
    LIMIT = 1000
    companies = await company_dao.get_all_companies(
        limit=LIMIT,
        user_id=current_user.id,
    )
    companies_dto = [
        CompanyDTO(
            name=company.name,
            tiker=company.tiker,
            type=CompanyTypeEnum(company.type),
            has_shares=False, # TODO заменить на высчитывание
            stops=[
                 CompanyStopDTO(
                    period=stop.period,
                    value=stop.value,
                )
                for stop in company.stops
            ],
        )
        for company in companies
    ]

    message = TAStartGenerateMessage(
        user_id=current_user.id,
        period=PeriodEnum(period),
        companies=companies_dto,
        update_db=update_db,
        send_message=send_messages,
        send_test_message=send_test_message,
    )

    payload_str = str(message.model_dump_json())
    logging.debug(f"********* payload_str: {payload_str}")
    result = start_generate_task.delay(payload_str)

    logging.debug(f"********* payload: {result}")

    res_message = TAMessageResponse(id=result.id, status=result.status)
    logging.info(f"********* Run generate result: {res_message}")

    return res_message


@router.get("/{task_id}")
def get_task_status(task_id: str) -> TAMessageStatus:
    task = start_generate_task.AsyncResult(task_id)
    logging.info(f"********* Get task result: {str(task)}")

    response = TAMessageStatus(id=task.id, status=task.status, result=task.result)
    logging.info(f"********* Get task message: {str(response)}")

    return response
