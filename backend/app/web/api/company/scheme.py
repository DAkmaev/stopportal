from enum import Enum
from typing import List, Optional

from app.web.api.stop.scheme import StopDTO
from pydantic import BaseModel


class CompanyTypeEnum(str, Enum):  # noqa: WPS600
    MOEX = "MOEX"
    YAHOO = "YAHOO"


class StrategiesInputDTO(BaseModel):
    id: int


class StrategiesDTO(StrategiesInputDTO):
    name: str


class CompanyModelDTO(BaseModel):
    id: int
    tiker: str
    name: Optional[str] = None
    type: CompanyTypeEnum
    stops: Optional[List[StopDTO]]
    strategies: Optional[List[StrategiesDTO]]


class CompanyModelInputDTO(BaseModel):
    tiker: str
    name: Optional[str] = None
    type: Optional[CompanyTypeEnum] = CompanyTypeEnum.MOEX
    strategies: Optional[List[StrategiesInputDTO]] = []


class CompanyModelPatchDTO(CompanyModelInputDTO):
    tiker: Optional[str] = None
    type: Optional[CompanyTypeEnum] = None
    strategies: Optional[List[StrategiesInputDTO]] = []
