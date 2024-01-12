from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from backend.db.models.briefcase import CurrencyEnum, RegistryOperationEnum


class BriefcaseInputDTO(BaseModel):
    id: Optional[int] = None
    fill_up: Optional[float] = None


class BriefcaseDTO(BriefcaseInputDTO):
    id: int


class BriefcaseCompanyDTO(BaseModel):
    id: int
    name: Optional[str] = None
    tiker: Optional[str] = None


class BriefcaseStrategyDTO(BaseModel):
    id: int
    name: Optional[str] = None


class BriefcaseItemInputDTO(BaseModel):
    count: int
    dividends: Optional[float] = None
    company: BriefcaseCompanyDTO
    strategy: Optional[BriefcaseStrategyDTO] = None


class BriefcaseItemDTO(BriefcaseItemInputDTO):
    id: int


class BriefcaseRegistryInputDTO(BaseModel):
    count: Optional[int] = None
    company: BriefcaseCompanyDTO
    strategy: Optional[BriefcaseStrategyDTO] = None
    amount: float
    price: Optional[float] = None
    currency: CurrencyEnum
    operation: RegistryOperationEnum


class BriefcaseRegistryDTO(BriefcaseRegistryInputDTO):
    id: int
    created_date: datetime
    briefcase: BriefcaseDTO

