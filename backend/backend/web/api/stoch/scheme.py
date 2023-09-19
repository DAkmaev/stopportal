from pydantic import BaseModel
from enum import Enum


class StochDecisionEnum(str, Enum):
    BUY = 'BUY'
    SELL = 'SELL'
    RELAX = 'RELAX'


class StochDecisionModel(BaseModel):
    """
    Scheme for Stoch decision.

    """

    tiker: str
    decision: StochDecisionEnum
    k: float
    d: float
    k_previous: float
    d_previous: float
