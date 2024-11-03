import os
from kombu import Queue

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")

task_queues = (
    Queue('run_calculation', routing_key='run_calculation'),
    Queue('ta_calculation', routing_key='ta_calculation'),
    Queue('ta_final', routing_key='ta_final'),
)

task_default_queue = 'default'
task_default_exchange_type = 'direct'
task_default_routing_key = 'default'

task_routes = {
    'tasks.add_task': {'queue': 'run_calculation'},
}
