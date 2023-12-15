from typing import Optional

from pydantic import BaseModel


class BriefcaseInputDTO(BaseModel):
    id: Optional[int] = None
    fill_up: float


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

