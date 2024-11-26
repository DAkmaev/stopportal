import asyncio
import logging
import nest_asyncio

from celery import group
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.dao.companies import CompanyDAO
from backend.app.db.dao.ta_decisions import TADecisionDAO
from backend.app.db.db import SessionLocal
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
nest_asyncio.apply()


@celery_app.task(name="start_generate_task")  # , queue='run_calculation')
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


@celery_app.task(name="ta_generate_task")  # (queue='ta_calculation')
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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            update_db_decisions(decisions=ta_decisions, user_id=params.user_id)
        )

    logger.info("********* Finish final task")


@celery_app.task(name="send_telegram_task")
def send_telegram_task(
    message: str,
):
    logger.info(f"Send message: '{message}'")
    send_sync_tg_message(message)


async def update_db_decisions(
    decisions: list[DecisionDTO],
    user_id: int,
    dbsession: AsyncSession = None,
):
    should_close_session = dbsession is None
    if should_close_session:
        dbsession = SessionLocal()

    decisions_dao = TADecisionDAO(session=dbsession)
    company_dao = CompanyDAO(session=dbsession)
    tasks = []
    for decision in decisions:
        company = await company_dao.get_company_model_by_tiker(
            tiker=decision.tiker, user_id=user_id
        )
        task = decisions_dao.update_or_create_ta_decision_model(
            company=company,
            period=decision.period,
            decision=decision.decision,
            k=decision.k,
            d=decision.d,
            last_price=decision.last_price,
        )
        tasks.append(task)

    await asyncio.gather(*tasks)

    if should_close_session:
        await dbsession.commit()
        await dbsession.close()
