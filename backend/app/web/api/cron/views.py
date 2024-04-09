from app.db.dao.user import UserDAO
from app.db.dependencies import get_sync_db_session
from app.schemas.ta import TAMessageResponse
from app.services.ta_bulk_service import TABulkService
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/ta/{user_id}")
async def cron_generate_ta_decisions(  # noqa: WPS211
    user_id: int,
    period: str = "All",
    send_messages: bool = True,
    update_db: bool = True,
    send_test_message: bool = False,
    user_dao: UserDAO = Depends(),
) -> TAMessageResponse:
    user = await user_dao.get_user(user_id=user_id)
    with get_sync_db_session() as db:
        ta_bulk_service = TABulkService(db)
        return ta_bulk_service.generate_ta_decisions(
            user_id=user.id,
            period=period,
            send_messages=send_messages,
            update_db=update_db,
            send_test_message=send_test_message,
        )
