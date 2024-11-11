import logging
from celery import Celery

from worker.src import settings

logger = logging.getLogger(__name__)

app = Celery('tasks')

app.config_from_object(settings.Settings())
