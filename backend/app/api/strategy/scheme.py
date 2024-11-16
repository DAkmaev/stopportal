from typing import Optional

from pydantic import BaseModel


class StrategiesInputDTO(BaseModel):
    name: str
    description: Optional[str]


class StrategiesDTO(StrategiesInputDTO):
    id: int
