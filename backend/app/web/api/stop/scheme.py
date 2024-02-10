from typing import Optional, List

from pydantic import BaseModel
from enum import Enum


class StopInputDTO(BaseModel):
    company_id: int
    period: str
    value: Optional[float] = None


class StopDTO(StopInputDTO):
    id: int
