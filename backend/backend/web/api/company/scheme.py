from typing import Optional, List

from pydantic import BaseModel
from enum import Enum


class CompanyTypeEnum(str, Enum):
    MOEX = 'MOEX'
    YAHOO = 'YAHOO'


class CompanyStopInputDTO(BaseModel):
    period: str
    value: float


class CompanyStopDTO(CompanyStopInputDTO):
    id: int


class CompanyModelDTO(BaseModel):
    """
    Scheme for company.
    """
    id: int
    tiker: str
    name: Optional[str] = None
    type: CompanyTypeEnum
    stops: Optional[List[CompanyStopDTO]]


class CompanyModelInputDTO(BaseModel):
    """DTO for creating new company model."""

    tiker: str
    name: Optional[str] = None
    type: Optional[CompanyTypeEnum] = CompanyTypeEnum.MOEX
    stops: Optional[List[CompanyStopInputDTO]] = []


class CompanyModelPatchDTO(CompanyModelInputDTO):
    """DTO for updating company model."""

    tiker: Optional[str] = None
    type: Optional[CompanyTypeEnum] = None
    stops: Optional[List[CompanyStopInputDTO]] = None


