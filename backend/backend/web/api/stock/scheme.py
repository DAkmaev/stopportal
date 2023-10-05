from typing import Optional, List

from pydantic import BaseModel
from enum import Enum


class StockTypeEnum(str, Enum):
    MOEX = 'MOEX'
    YAHOO = 'YAHOO'


class StockStopInputDTO(BaseModel):
    period: str
    value: float


class StockStopDTO(StockStopInputDTO):
    id: int


class StockModelDTO(BaseModel):
    """
    Scheme for Stock.
    """
    id: int
    tiker: str
    type: StockTypeEnum
    stops: Optional[List[StockStopDTO]]


class StockModelInputDTO(BaseModel):
    """DTO for creating new stock model."""

    tiker: str
    type: Optional[StockTypeEnum] = StockTypeEnum.MOEX



