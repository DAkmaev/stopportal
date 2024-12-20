from fastapi.routing import APIRouter
from backend.app.api import (  # noqa: WPS235
    monitoring,
    user,
    login,
    company,
    stop,
    strategy,
    briefcase,
    ta,
    internal,
)

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(company.router, prefix="/companies", tags=["companies"])
api_router.include_router(stop.router, prefix="/stops", tags=["stops"])
api_router.include_router(strategy.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(briefcase.router, prefix="/briefcases", tags=["briefcase"])

api_router.include_router(ta.router, prefix="/tas", tags=["tas"])
api_router.include_router(internal.router, prefix="/internal", tags=["internal"])
