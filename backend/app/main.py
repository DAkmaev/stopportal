import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from backend.app.settings import settings
from backend.app.api.router import api_router
from backend.app.db.db import init_db

logging.basicConfig(
    level=logging.getLevelName(settings.log_level.value),
    format="%(levelname)s:     %(message)s",  # noqa: WPS323
    # format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",  # noqa: WPS323
)
logger = logging.getLogger("stopportal")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App startup")
    await init_db(app)
    yield
    logger.info("App shutdown")


app = FastAPI(
    logging=logging,
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# Main router for the API.
app.include_router(router=api_router, prefix="/api")


# if __name__ == "__main__":
#     uvicorn.run(app, host='0.0.0.0', port=80)
