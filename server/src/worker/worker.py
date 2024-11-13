import logging
from celery import Celery

from server.src.settings import settings

logger = logging.getLogger(__name__)


celery_app = Celery("tasks")

celery_app.conf.broker_url = settings.celery_broker_url
celery_app.conf.result_backend = settings.celery_backend_url
