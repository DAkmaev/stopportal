from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DECIMAL, Integer

from backend.db.base import Base
from backend.db.models.company import CompanyModel, StrategyModel


class BriefcaseModel(Base):
    """Model for Briefcase."""

    __tablename__ = "briefcases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fill_up: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL, nullable=True)
    items: Mapped[List["BriefcaseItemModel"]] = relationship(lazy="selectin",
                                                    cascade="all,delete")


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
    briefcase_id: Mapped[int] = mapped_column(ForeignKey("briefcases.id"))


# class BriefcaseRegistryItemModel(Base):
#     """Model for BriefcaseRegistryItem."""
#
#     __tablename__ = "briefcase_registry_items"
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     datetime: [datetime]
#     company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
#     company: Mapped['CompanyModel'] = relationship(lazy="selectin")
#     count: Mapped[int] = mapped_column(Integer)
#     amount: Mapped[DECIMAL] = mapped_column(DECIMAL, nullable=True)
#
#     strategy_id: Mapped[int] = mapped_column(ForeignKey("strategies.id"), nullable=True)
#     strategy: Mapped[Optional['StrategyModel']] = relationship()
#
#     валюта
#     type (тип операции)
#
#     briefcase_id: Mapped[int] = mapped_column(ForeignKey("briefcases.id"))

