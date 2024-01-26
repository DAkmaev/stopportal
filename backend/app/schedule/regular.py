from fastapi_restful.tasks import repeat_every

from app.web.application import get_app

app = get_app()


@app.on_event("startup")
@repeat_every(seconds=10)
def test_task() -> None:
    print('#######')
