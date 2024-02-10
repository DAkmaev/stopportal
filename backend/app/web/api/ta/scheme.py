from typing import Optional

from pydantic import BaseModel
from enum import Enum


class TADecisionEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    RELAX = "RELAX"
    UNKNOWN = "UNKNOWN"


class TAPeriodEnum(str, Enum):
    DAY = "D"
    WEEK = "W"
    MONTH = "M"
    ALL = "All"


class TACompanyDTO(BaseModel):
    id: int
    name: str
    tiker: str


class TADecisionDTO(BaseModel):
    """
    Scheme for TA decision.

    """

    company: TACompanyDTO
    decision: TADecisionEnum
    # last_price: Optional[float] = None
    k: Optional[float] = None
    d: Optional[float] = None
    period: str
    # k_previous: Optional[float] = None
    # d_previous: Optional[float] = None
