from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DECIMAL, Integer

from backend.db.base import Base
from backend.db.models.company import CompanyModel, StrategyModel


class BriefcaseModel(Base):
    """Model for Briefcase."""

    __tablename__ = "briefcases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fill_up: Mapped[DECIMAL] = mapped_column(DECIMAL, nullable=True)


class BriefcaseItemModel(Base):
    """Model for BriefcaseItem."""

    __tablename__ = "briefcase_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    count: Mapped[int] = mapped_column(Integer)
    dividends: Mapped[DECIMAL] = mapped_column(DECIMAL, nullable=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    strategy_id: Mapped[int] = mapped_column(ForeignKey("strategies.id"), nullable=True)
    company: Mapped['CompanyModel'] = relationship(lazy="selectin")
    strategy: Mapped[Optional['StrategyModel']] = relationship()

