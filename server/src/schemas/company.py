from pydantic import BaseModel

from server.src.schemas.enums import PeriodEnum, CompanyTypeEnum


class CompanyStop(BaseModel):
    period: PeriodEnum
    value: float


class CompanyDTO(BaseModel):
    name: str
    tiker: str
    type: str = CompanyTypeEnum.MOEX
    has_shares: bool = False
    stops: list[CompanyStop] | None = None