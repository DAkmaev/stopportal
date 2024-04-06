from celery import Celery
from app.settings import settings

redis_url = settings.redis_url

celery_app = Celery("tasks", broker=redis_url, backend=redis_url)
