import logging

from fastapi import APIRouter, Depends

from backend.app.schemas.ta import TAMessageResponse
from backend.app.services.ta_service import TAService
from backend.app.worker.tasks import start_generate_task

router = APIRouter()


@router.get("/ta/{user_id}")
async def internal_start_generate_ta_decisions(  # noqa: WPS211
    user_id: int,
    period: str = "All",
    send_messages: bool = True,
    update_db: bool = True,
    send_test_message: bool = False,
    ta_service: TAService = Depends(),
) -> TAMessageResponse:
    message = await ta_service.fill_send_start_generate_message(
        user_id=user_id,
        period=period,
        send_messages=send_messages,
        update_db=update_db,
        send_test_message=send_test_message,
    )

    payload_str = str(message.model_dump_json())
    result = start_generate_task.delay(payload_str)
    logging.debug(f"********* payload: {result}")

    return TAMessageResponse(id=result.id, status=result.status)
