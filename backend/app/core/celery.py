from celery import Celery

from app.settings import settings

redis_url = 'redis://localhost:6379' # settings.redis_url

celery_app = Celery(__name__, broker=redis_url, backend=redis_url)

