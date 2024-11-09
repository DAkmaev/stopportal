from pydantic import BaseModel

from worker.src.dto.enums import CompanyTypeEnum, PeriodEnum


class CompanyStop(BaseModel):
    period: PeriodEnum
    value: float


class CompanyDTO(BaseModel):
    name: str
    tiker: str
    type: str = CompanyTypeEnum.MOEX
    has_shares: bool = False
    stops: list[CompanyStop] | None = None