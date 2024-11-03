import pytest
from celery import Celery


@pytest.fixture
def celery_app():
    app = Celery('tasks', broker='memory://', backend='memory://')
    app.conf.task_always_eager = True
    return app
