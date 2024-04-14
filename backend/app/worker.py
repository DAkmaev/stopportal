import logging

from app.core.celery import celery_app
from app.db.dependencies import get_sync_db_session
from app.schemas.ta import TADecisionDTO, TAFinalMessage, TAGenerateMessage
from app.services.ta_sync_service import TAService
from app.utils.telegram.telegramm_sync_client import send_sync_tg_message
from pydantic import TypeAdapter

logger = logging.getLogger(__name__)


def generate_decision(
    message: TAGenerateMessage,
):
    with get_sync_db_session() as db:
        ta_service = TAService(db)
        decisions = ta_service.generate_ta_decision(
            tiker=message.tiker,
            user_id=message.user_id,
            period=message.period,
        )
        if message.send_message:
            ta_service.send_tg_messages(decisions.values())

        if message.update_db:
            ta_service.update_ta_models(decisions.values())
            db.commit()

        logger.info(
            f"Завершена генерация TA для {message.tiker} для пользователя {message.user_id}",
        )
        return [dec.model_dump_json() for dec in decisions.values()]


@celery_app.task
def ta_generate_task(
    message_json: str,
):
    ta_message: TAGenerateMessage = TypeAdapter(TAGenerateMessage).validate_json(
        message_json,
    )
    return generate_decision(ta_message)


@celery_app.task
def ta_final_task(  # noqa:  WPS210
    results: list,
    params_json: str,
):
    params: TAFinalMessage = TypeAdapter(TAFinalMessage).validate_json(params_json)
    logger.info(f"Завершена генерация TA для пользователя {params.user_id}")
    ta_decisions = [
        TypeAdapter(TADecisionDTO).validate_json(ta_json)
        for sublist in results
        for ta_json in sublist
    ]

    with get_sync_db_session() as db:
        ta_service = TAService(db)

        if params.update_db:
            for ta_decision in ta_decisions:
                ta_service.update_ta_model(ta_decision)

            db.commit()

        if params.send_message:
            messages = ta_service.generate_bulk_tg_messages(
                ta_decisions,
                params.send_test_message,
            )
            for message in messages:
                send_telegram_task.delay(message)


@celery_app.task
def send_telegram_task(
    message: str,
):
    send_sync_tg_message(message)
