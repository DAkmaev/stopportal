from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String, Float

from backend.db.base import Base

if TYPE_CHECKING:
    from .item import Item  # noqa: F401


class CompanyModel(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tiker: Mapped[str] = mapped_column(String, index=True, unique=True)
    type: Mapped[str] = mapped_column(String, default='MOEX', nullable=True)
    stops: Mapped[List["CompanyStopModel"]] = relationship(lazy="selectin")


class CompanyStopModel(Base):
    __tablename__ = "companies_stop"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))

