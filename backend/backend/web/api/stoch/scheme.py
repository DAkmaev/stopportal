from typing import Optional

from pydantic import BaseModel
from enum import Enum


class StochDecisionEnum(str, Enum):
    BUY = 'BUY'
    SELL = 'SELL'
    RELAX = 'RELAX'
    UNKNOWN = 'UNKNOWN'


class StochDecisionModel(BaseModel):
    """
    Scheme for Stoch decision.

    """

    tiker: str
    decision: StochDecisionEnum
    last_price: Optional[float] = None
    k: Optional[float] = None
    d: Optional[float] = None
    stop: Optional[float] = None
    # k_previous: Optional[float] = None
    # d_previous: Optional[float] = None
