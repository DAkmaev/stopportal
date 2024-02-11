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
    # last_price: Optional[float] = None
    k: Optional[float] = None  # noqa: WPS111
    d: Optional[float] = None  # noqa: WPS111
    period: str
    # k_previous: Optional[float] = None
    # d_previous: Optional[float] = None
