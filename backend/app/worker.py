import logging

from pydantic import TypeAdapter

from app.core.celery import celery_app
from app.db.dependencies import get_sync_db_session
from app.schemas.Ta import TADecisionDTO
from app.services.ta_sync_service import TAService

logger = logging.getLogger(__name__)


def generate_decision(
    tiker,
    user_id,
    period,
    send_message,
    update_db,
):
    with get_sync_db_session() as db:
        ta_service = TAService(db)
        decisions = ta_service.generate_ta_decision(
            tiker=tiker,
            user_id=user_id,
            period=period,
        )
        if send_message:
            ta_service.send_tg_messages(decisions.values())

        if update_db:
            ta_service.update_ta_models(decisions.values())
            db.commit()


        logger.info(f'Завершена генерация TA для {tiker} для пользователя {user_id}')
        result_json = [dec.model_dump_json() for dec in decisions.values()]

        return result_json


@celery_app.task
def ta_generate_task(
    tiker: str,
    user_id: int,
    period: str,
    send_message: bool = False,
    update_db: bool = False,
):
    result = generate_decision(tiker, user_id, period, send_message, update_db)
    return result


@celery_app.task
def ta_task(
    tiker: str,
    user_id: int,
    period: str,
    send_message: bool,
):
    return f"Execute task for {tiker}!"


@celery_app.task
def ta_final_task(
    results: list,
    user_id: int,
    send_message: bool,
    update_db: bool,
    send_test_message: bool,
):
    logger.info(f'Завершена генерация TA для пользователя {user_id}')
    ta_decisions = [TypeAdapter(TADecisionDTO).validate_json(ta_json) for sublist in results for ta_json in sublist]

    with get_sync_db_session() as db:
        ta_service = TAService(db)

        if update_db:
            for ta_decision in ta_decisions:
                ta_service.update_ta_model(ta_decision)

            db.commit()

        if send_message:
            ta_service.send_bulk_tg_messages(ta_decisions, send_test_message)
