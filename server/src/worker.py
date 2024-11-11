import logging
from celery import Celery

from server.src.settings import settings

logger = logging.getLogger(__name__)

app = Celery('tasks_server')

app.config_from_object(settings)


# @app.task(queue='ta_save_results')
# def ta_save_results_task(
#         message_json: str,
#         user_id: int,
# ):
#
#     logger.info(
#         f"Результат генерации: {message_json} для пользователя {user_id}",
#     )
