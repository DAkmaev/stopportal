from typing import Optional

from pydantic import BaseModel


class StopInputDTO(BaseModel):
    company_id: int
    period: str
    value: Optional[float] = None


class StopDTO(StopInputDTO):
    id: int
