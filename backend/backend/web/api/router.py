from fastapi.routing import APIRouter

from backend.web.api import docs, dummy, echo, monitoring, user, stoch, company, cron_job_run, strategy

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(stoch.router, prefix="/stoch", tags=["stoch"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(strategy.router, prefix="/strategy", tags=["strategy"])
api_router.include_router(cron_job_run.router, prefix="/cron_job_run", tags=["cron_job_run"])

