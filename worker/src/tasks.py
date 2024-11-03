import logging
from celery import Celery
import time

from worker import settings

logger = logging.getLogger(__name__)

app = Celery('tasks')

app.config_from_object(settings)


@app.task(queue='run_calculation')
def add_task(x, y):
    time.sleep(1)
    return x + y
