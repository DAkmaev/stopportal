# import logging
#
# from app.web.api.dummy.scheme import TAMessageResponse
# from fastapi import APIRouter
#
# from app.web.deps import CurrentUser
# from app.worker import ta_generate_task
#
# router = APIRouter()
# logger = logging.getLogger(__name__)
#
#
# @router.post("/{tiker}")
# async def generate_ta_decision(
#     tiker: str,
#     current_user: CurrentUser,
#     period: str = "All",
#     send_messages: bool = True,
# ) -> TAMessageResponse:
#     user_id = current_user.id
#     #logger.info(user_id)
#     r = ta_generate_task.delay(
#             tiker,
#             user_id,
#             period,
#     )
#     return TAMessageResponse(id=r.task_id, status=r.status)
