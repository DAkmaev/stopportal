import logging
import time

from worker.src.worker import app

logger = logging.getLogger(__name__)


@app.task(queue='run_calculation')
def add_task(x, y):
    time.sleep(1)
    return x + y
