import json
import logging

from celery import group
from pydantic import TypeAdapter

from backend.app.utils.ta.ta_client import send_update_db_request
from backend.app.services.ta_service import TAService
from backend.app.utils.telegram.telegramm_client import send_sync_tg_message
from backend.app.schemas.ta import (
    TAGenerateMessage,
    TAFinalMessage,
    DecisionDTO,
)
from backend.app.schemas.ta import TAStartGenerateMessage
from backend.app.worker.worker import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="start_generate_task")
def start_generate_task(
    message_json: str,
):
    message: TAStartGenerateMessage = TypeAdapter(TAStartGenerateMessage).validate_json(
        message_json,
    )

    task_group = group(
        ta_generate_task.s(
            TAGenerateMessage(
                company=company,
                period=message.period,
            ).model_dump_json(),
            message.user_id,
        )
        for company in message.companies
    )
    task_chain = task_group | ta_final_task.s(
        TAFinalMessage(
            user_id=message.user_id,
            send_test_message=message.send_test_message,
            send_message=message.send_message,
            update_db=message.update_db,
        ).model_dump_json(),
    )

    task_chain.delay()


@celery_app.task(name="ta_generate_task")
def ta_generate_task(
    message_json: str,
    user_id: int,
):
    message: TAGenerateMessage = TypeAdapter(TAGenerateMessage).validate_json(
        message_json,
    )

    ta_service = TAService()
    try:
        decisions = ta_service.generate_ta_decision(
            company=message.company,
            period=message.period,
        )
    except Exception as exception:
        error_message = (
            f"Failed to generate decisions for company: {message.company.tiker}, "
            f"user_id: {user_id}, period: {message.period}. "
            f"Error: '{exception}'"
        )
        logger.error(error_message)
        decisions = {}

    logger.info(
        f"Завершена генерация TA для {message.company.name} для пользователя {user_id}",
    )
    return [dec.model_dump_json() for dec in decisions.values()]


@celery_app.task(name="ta_final_task")
def ta_final_task(  # noqa:  WPS210ß
    results: list,
    params_json: str,
):
    logging.debug(f"********* Final task params: {params_json}")
    params: TAFinalMessage = TypeAdapter(TAFinalMessage).validate_json(params_json)

    logger.info("********* Start final task...")
    ta_decisions = [
        TypeAdapter(DecisionDTO).validate_json(dec_json)
        for sublist in results
        for dec_json in sublist
    ]

    if params.send_message:
        logging.debug(f"********* Final task decisions: {ta_decisions}")
        messages = TAService().generate_bulk_tg_messages(
            ta_decisions,
            params.send_test_message,
        )
        logging.debug(f"********* Final task messages: {messages}")
        for message in messages:
            send_telegram_task.delay(message)

    if params.update_db:
        logging.info("********* Final task start saving to DB...")
        decisions_json = [dec.model_dump() for dec in ta_decisions]
        update_db_task.delay(json.dumps(decisions_json), params.user_id)

    logger.info("********* Finish final task")


@celery_app.task(name="send_telegram_task")
def send_telegram_task(
    message: str,
):
    logger.info(f"Send message: '{message}'")
    send_sync_tg_message(message)


@celery_app.task(name="update_db_task")
def update_db_task(
    decisions_str: str,
    user_id: int,
):
    logger.debug(f"Send update DB message: '{decisions_str}'")
    decisions_json = json.loads(decisions_str)
    send_update_db_request(decisions_json, user_id=user_id)


@celery_app.task(ignore_result=True)
def say_hello(who: str):
    print(f"Hello {who}")
