from app.core.celery import celery_app
from app.db.dependencies import get_sync_db_session
from app.services.ta_sync_service import TAService


def generate_decision(
    tiker,
    user_id,
    period,
    send_message,
):
    with get_sync_db_session() as db:
        ta_service = TAService(db)
        ta_service.generate_ta_decision(
            tiker=tiker,
            user_id=user_id,
            period=period,
            send_message=send_message,
        )

        db.commit()

        return f'Generated decision for {tiker}!'


@celery_app.task
def ta_generate_task(
    tiker: str,
    user_id: int,
    period: str,
    send_message: bool,
):
    result = generate_decision(tiker, user_id, period, send_message)
    return result


@celery_app.task
def ta_generate_tasks(
    user_id: int,
    period: str,
    send_message: bool,
):
    result = generate_decisions(user_id, period, send_message)
    return result

