from fastapi.routing import APIRouter

from backend.web.api import (docs, dummy, echo, monitoring,
                             stoch, company, cron_job_run, strategy, stop, briefcase,
                             login, auth)

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(stoch.router, prefix="/stoch", tags=["stoch"])
api_router.include_router(company.router, prefix="/companies", tags=["companies"])
api_router.include_router(stop.router, prefix="/stops", tags=["stops"])
api_router.include_router(strategy.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(cron_job_run.router, prefix="/cron_job_run", tags=["cron_job_run"])
api_router.include_router(briefcase.router, prefix="/briefcase", tags=["briefcase"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

