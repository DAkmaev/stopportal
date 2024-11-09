import pytest
from celery import Celery


@pytest.fixture
def celery_app():
    app = Celery('tasks', broker='memory://', backend='memory://')
    app.conf.task_always_eager = True
    return app


@pytest.fixture
def celery_local_app():
    app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/1')
    app.conf.update(
        task_always_eager=False,  # Отключаем eager-режим
        task_eager_propagates=True,
        task_store_eager_result=False,
        task_ignore_result=False,
        task_store_errors_even_if_ignored=True
    )
    return app
