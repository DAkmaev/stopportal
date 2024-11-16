from typing import List, Optional

from backend.app.api.stop.scheme import StopDTO
from pydantic import BaseModel

from backend.app.schemas.enums import CompanyTypeEnum


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
