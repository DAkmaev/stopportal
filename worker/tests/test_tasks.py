from worker.src.tasks import add_task


def test_add_task(celery_app):
    result = add_task.apply((10, 20), queue='run_calculation')
    assert result.successful()
    assert result.result == 30
