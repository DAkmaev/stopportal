import logging

from app.web.api.dummy.scheme import Dummy
from fastapi import APIRouter

from app.web.deps import CurrentUser
from app.worker import dummy_task

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
async def send_dummy_task(
    current_user: CurrentUser,
) -> Dummy:
    #user_id = current_user.id
    #logger.info(user_id)
    r = dummy_task.delay()
    return Dummy(id=r.task_id, status=r.status)
