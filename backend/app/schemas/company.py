from pydantic import BaseModel

from backend.app.schemas.enums import PeriodEnum, CompanyTypeEnum


class CompanyStopDTO(BaseModel):
    period: PeriodEnum
    value: float


class CompanyDTO(BaseModel):
    name: str
    tiker: str
    type: str = CompanyTypeEnum.MOEX
    has_shares: bool = False
    stops: list[CompanyStopDTO] | None = None
