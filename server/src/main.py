import logging

from fastapi import FastAPI
from server.src.settings import settings
from server.src.api.router import api_router
from server.src.db.db import init_db

logging.basicConfig(
    level=logging.getLevelName(settings.log_level.value),
    format="%(levelname)s:     %(message)s",  # noqa: WPS323
    #format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",  # noqa: WPS323
)
logger = logging.getLogger("stopportal")


app = FastAPI(
    logging=logging,
)


@app.on_event("startup")
async def on_startup():
    logger.info("Startup block")
    await init_db(app)

# Main router for the API.
app.include_router(router=api_router, prefix="/api")

