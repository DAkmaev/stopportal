from fastapi.routing import APIRouter
from app.web.api import (  # noqa: WPS235
    docs,
    monitoring,
    login,
    user,
    ta,
    company,
    cron_job_run,
    strategy,
    stop,
    briefcase,
    cron,
)

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(company.router, prefix="/companies", tags=["companies"])
api_router.include_router(stop.router, prefix="/stops", tags=["stops"])
api_router.include_router(strategy.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(
    cron_job_run.router,
    prefix="/cron_job_run",
    tags=["cron_job_run"],
)
api_router.include_router(briefcase.router, prefix="/briefcase", tags=["briefcase"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(cron.router, prefix="/cron", tags=["cron"])
api_router.include_router(ta.router, prefix="/ta", tags=["ta"])
