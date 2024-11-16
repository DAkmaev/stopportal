from datetime import datetime
from typing import Optional

from backend.app.db.models.briefcase import CurrencyEnum, RegistryOperationEnum
from pydantic import BaseModel


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


class BriefcaseRegistryInputDTO(BaseModel):
    count: Optional[int] = None
    company: BriefcaseCompanyDTO
    strategy: Optional[BriefcaseStrategyDTO] = None
    amount: float
    price: Optional[float] = None
    currency: CurrencyEnum
    operation: RegistryOperationEnum
    created_date: Optional[datetime] = None


class BriefcaseRegistryDTO(BriefcaseRegistryInputDTO):
    id: int
    created_date: datetime
    briefcase: BriefcaseDTO
