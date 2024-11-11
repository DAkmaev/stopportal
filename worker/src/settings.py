import os
from typing import Tuple, Dict

from kombu import Queue
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    broker_url: str = 'redis://localhost:6379/0'

    # task_queues: Tuple[Queue, ...] = (
    #     Queue('run_calculation', routing_key='run_calculation.#'),
    #     Queue('ta_calculation', routing_key='ta_calculation'),
    #     Queue('ta_final', routing_key='ta_final'),
    # )

    task_default_queue: str = 'default'
    task_default_exchange_type: str = 'direct'
    task_default_routing_key: str = 'default'

    # task_routes: Dict[str, Dict[str, str]] = {
    #     'tasks.add_task': {'queue': 'run_calculation'},
    # }

    # Telegram
    chat_id: str = ''
    bot_token: str = ''


settings = Settings()
