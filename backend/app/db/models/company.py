from typing import TYPE_CHECKING, List, Optional

from app.db.base import Base
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Float, String

from .user import UserModel

if TYPE_CHECKING:
    from .item import Item  # noqa: F401,WPS300


association_table = Table(
    "companies_strategies",
    Base.metadata,
    Column("company_id", ForeignKey("companies.id"), primary_key=True),
    Column("strategy_id", ForeignKey("strategies.id"), primary_key=True),
)


class CompanyModel(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=True)
    tiker: Mapped[str] = mapped_column(String, index=True, unique=True)
    type: Mapped[str] = mapped_column(String, default="MOEX", nullable=True)
    stops: Mapped[List["StopModel"]] = relationship(
        lazy="selectin",
        cascade="all,delete",
    )
    strategies: Mapped[List["StrategyModel"]] = relationship(
        secondary=association_table,
        back_populates="companies",
        lazy="selectin",
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True, nullable=True)
    user: Mapped[Optional["UserModel"]] = relationship()


class StopModel(Base):
    __tablename__ = "companies_stop"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))


class StrategyModel(Base):
    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    companies: Mapped[List["CompanyModel"]] = relationship(
        secondary=association_table,
        back_populates="strategies",
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True, nullable=True)
    user: Mapped[Optional["UserModel"]] = relationship()
