from typing import Optional, List

from pydantic import BaseModel
from enum import Enum

from app.web.api.stop.scheme import StopInputDTO, StopDTO


class CompanyTypeEnum(str, Enum):
    MOEX = "MOEX"
    YAHOO = "YAHOO"


class StrategiesInputDTO(BaseModel):
    id: int


class StrategiesDTO(StrategiesInputDTO):
    name: str


class CompanyModelDTO(BaseModel):
    """
    Scheme for company.
    """

    id: int
    tiker: str
    name: Optional[str] = None
    type: CompanyTypeEnum
    stops: Optional[List[StopDTO]]
    strategies: Optional[List[StrategiesDTO]]


class CompanyModelInputDTO(BaseModel):
    """DTO for creating new company model."""

    tiker: str
    name: Optional[str] = None
    type: Optional[CompanyTypeEnum] = CompanyTypeEnum.MOEX
    strategies: Optional[List[StrategiesInputDTO]] = []


class CompanyModelPatchDTO(CompanyModelInputDTO):
    """DTO for updating company model."""

    tiker: Optional[str] = None
    type: Optional[CompanyTypeEnum] = None
    strategies: Optional[List[StrategiesInputDTO]] = []
