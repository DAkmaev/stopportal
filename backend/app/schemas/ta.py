from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TADecisionEnum(str, Enum):  # noqa: WPS600
    BUY = "BUY"
    SELL = "SELL"
    RELAX = "RELAX"
    UNKNOWN = "UNKNOWN"


class TAPeriodEnum(str, Enum):  # noqa: WPS600
    DAY = "D"
    WEEK = "W"
    MONTH = "M"
    ALL = "All"


class TACompanyDTO(BaseModel):
    id: int
    name: str
    tiker: str


class TADecisionDTO(BaseModel):
    company: TACompanyDTO
    decision: TADecisionEnum
    last_price: Optional[float] = None
    k: Optional[float] = None  # noqa: WPS111
    d: Optional[float] = None  # noqa: WPS111
    period: TAPeriodEnum
    # k_previous: Optional[float] = None
    # d_previous: Optional[float] = None


class TAGenerateMessage(BaseModel):
    tiker: str
    user_id: int
    period: TAPeriodEnum
    send_message: bool = False
    update_db: bool = False


class TAFinalMessage(BaseModel):
    user_id: int
    send_message: bool
    update_db: bool
    send_test_message: bool


class TAMessageResponse(BaseModel):
    id: str
    status: str


class TAMessageStatus(TAMessageResponse):
    id: str
    status: str
    result: str
