# from datetime import datetime
# from enum import Enum
#
# from pydantic import BaseModel
#
#
# class TAPeriodEnum(str, Enum):  # noqa: WPS600
#     DAY = "D"
#     WEEK = "W"
#     MONTH = "M"
#     ALL = "All"
#
#
# class TAMessage(BaseModel):
#     tiker: str
#     user_id: int
#     period: TAPeriodEnum
#
#
# class TAMessageResponse(BaseModel):
#     id: str
#     status: str
