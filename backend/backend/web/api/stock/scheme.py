from pydantic import BaseModel
from enum import Enum


class StockTypeEnum(str, Enum):
    MOEX = 'MOEX'
    YAHOO = 'YAHOO'


class StockModelDTO(BaseModel):
    """
    Scheme for Stock.
    """
    id: int
    tiker: str
    type: StockTypeEnum


class StockModelInputDTO(BaseModel):
    """DTO for creating new stock model."""

    tiker: str
    type: StockTypeEnum
