import logging

from app.core.celery import celery_app
from app.db.dao.sync.briefcase_sync import BriefcaseSyncDAO
from app.db.dao.sync.company_sync import TACompanySyncDAO
from app.db.dao.sync.decisions_sync import TADecisionSyncDAO
from app.db.dependencies import get_sync_db_session
from app.schemas.ta import TADecisionDTO, TAFinalMessage, TAGenerateMessage
from app.services.ta_sync_service import TAService
from app.utils.telegram.telegramm_sync_client import send_sync_tg_message
from pydantic import TypeAdapter

logger = logging.getLogger(__name__)


def generate_decision(  # noqa: WPS210
    message: TAGenerateMessage,
):
    with get_sync_db_session() as db:
        ta_service = TAService()
        company_dao = TACompanySyncDAO(db)
        company = company_dao.get_company(message.tiker, message.user_id)
        decisions = ta_service.generate_ta_decision(
            company,
            period=message.period,
        )
        if message.send_message:
            ta_service.send_tg_messages(decisions.values())

        if message.update_db:
            decision_dao = TADecisionSyncDAO(db)
            decision_dao.update_ta_models(decisions.values())
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

    ta_service = TAService()
    with get_sync_db_session() as db:
        if params.update_db:
            dao = TADecisionSyncDAO(db)
            for ta_decision in ta_decisions:
                dao.update_ta_model(ta_decision)

            db.commit()

        if params.send_message:
            brief_dao = BriefcaseSyncDAO(db)
            briefcase = brief_dao.get_briefcase_model_by_user_id(params.user_id)
            shares = brief_dao.get_all_briefcase_shares(briefcase.id)
            messages = ta_service.generate_bulk_tg_messages(
                ta_decisions,
                params.send_test_message,
                shares,
            )
            for message in messages:
                send_telegram_task.delay(message)


@celery_app.task
def send_telegram_task(
    message: str,
):
    send_sync_tg_message(message)
