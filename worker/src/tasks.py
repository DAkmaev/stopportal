import logging

from celery import group
from pydantic import TypeAdapter

from worker.src.services.ta_service import TAService
from worker.src.utils.telegram.telegramm_client import send_sync_tg_message
from worker.src.dto.ta import TAGenerateMessage, TAFinalMessage, DecisionDTO, TAMessageResponse
from worker.src.dto.ta import TAStartGenerateMessage
from worker.src.worker import app


logger = logging.getLogger(__name__)


@app.task(name='start_generate_task') #, queue='run_calculation')
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
        message.user_id,
    )

    result = task_chain.apply_async()

    return TAMessageResponse(id=result.id, status=result.status)


@app.task #(queue='ta_calculation')
def ta_generate_task(
        message_json: str,
        user_id: int,
):
    message: TAGenerateMessage = TypeAdapter(TAGenerateMessage).validate_json(
        message_json,
    )

    ta_service = TAService()
    decisions = ta_service.generate_ta_decision(
        company=message.company,
        period=message.period,
    )

    logger.info(
        f"Завершена генерация TA для {message.company.name} для пользователя {user_id}",
    )
    return [dec.model_dump_json() for dec in decisions.values()]


@app.task
def ta_final_task(  # noqa:  WPS210
    results: list,
    params_json: str,
):
    params: TAFinalMessage = TypeAdapter(TAFinalMessage).validate_json(params_json)
    logger.info(f"Старт final task...")
    ta_decisions = [
        TypeAdapter(DecisionDTO).validate_json(dec_json)
        for sublist in results
        for dec_json in sublist
    ]

    ta_service = TAService()
    if params.send_message:
        messages = ta_service.generate_bulk_tg_messages(
            ta_decisions,
            params.send_test_message,
        )
        for message in messages:
            send_telegram_task.delay(message)


@app.task
def send_telegram_task(
    message: str,
):
    logger.info(f"Send message: '{message}'")
    send_sync_tg_message(message)