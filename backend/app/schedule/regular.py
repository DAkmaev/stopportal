from app.web.application import get_app
from fastapi_restful.tasks import repeat_every

app = get_app()


@app.on_event("startup")
@repeat_every(seconds=10)
def test_task() -> None:
    print("#######")
