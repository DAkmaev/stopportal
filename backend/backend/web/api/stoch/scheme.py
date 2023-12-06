from typing import Optional

from pydantic import BaseModel
from enum import Enum


class StochDecisionEnum(str, Enum):
    BUY = 'BUY'
    SELL = 'SELL'
    RELAX = 'RELAX'
    UNKNOWN = 'UNKNOWN'


class StochPeriodEnum(str, Enum):
    DAY = 'D'
    WEEK = 'W'
    MONTH = 'M'
    ALL = 'All'


class StochCompanyDTO(BaseModel):
    id: int
    name: str
    tiker: str


class StochDecisionDTO(BaseModel):
    """
    Scheme for Stoch decision.

    """
    company: StochCompanyDTO
    decision: StochDecisionEnum
    last_price: Optional[float] = None
    k: Optional[float] = None
    d: Optional[float] = None
    period: str
    # k_previous: Optional[float] = None
    # d_previous: Optional[float] = None
