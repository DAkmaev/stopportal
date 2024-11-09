from enum import Enum
from typing import Optional

from pydantic import BaseModel

from worker.src.dto.enums import DecisionEnum, PeriodEnum
from worker.src.dto.company import CompanyDTO


class DecisionDTO(BaseModel):
    tiker: str
    decision: DecisionEnum
    last_price: Optional[float] = None
    k: Optional[float] = None  # noqa: WPS111
    d: Optional[float] = None  # noqa: WPS111
    period: PeriodEnum
    # k_previous: Optional[float] = None
    # d_previous: Optional[float] = None


class TAStartGenerateMessage(BaseModel):
    user_id: int
    period: PeriodEnum
    update_db: bool = False
    send_message: bool = False
    send_test_message: bool = False
    companies: list[CompanyDTO]


class TAGenerateMessage(BaseModel):
    period: PeriodEnum
    company: CompanyDTO


class TAFinalMessage(BaseModel):
    user_id: int
    send_message: bool
    update_db: bool
    send_test_message: bool


class TAMessageResponse(BaseModel):
    id: str
    status: str


class TAMessageStatus(TAMessageResponse):
    id: str
    status: str
    result: str
