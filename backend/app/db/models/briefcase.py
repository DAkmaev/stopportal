import enum
from typing import Optional

from app.db.base import Base
from app.db.models.company import CompanyModel, StrategyModel
from app.db.models.user import UserModel
from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DECIMAL, TIMESTAMP, Integer


class CurrencyEnum(enum.Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class RegistryOperationEnum(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDENDS = "DIVIDENDS"


class BriefcaseModel(Base):
    """Model for Briefcase."""

    __tablename__ = "briefcases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fill_up: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL, nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        index=True,
        nullable=True,
    )
    user: Mapped[Optional["UserModel"]] = relationship()


class BriefcaseRegistryModel(Base):
    """Model for BriefcaseRegistryItem."""

    __tablename__ = "briefcase_registry"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    currency: Mapped[str] = mapped_column(Enum(CurrencyEnum), default=CurrencyEnum.RUB)
    operation: Mapped[str] = mapped_column(Enum(RegistryOperationEnum))
    count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    amount: Mapped[DECIMAL] = mapped_column(DECIMAL, nullable=True)  # Сумма сделки
    price: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL, nullable=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["CompanyModel"] = relationship(lazy="selectin")

    strategy_id: Mapped[int] = mapped_column(ForeignKey("strategies.id"), nullable=True)
    strategy: Mapped[Optional["StrategyModel"]] = relationship(lazy="selectin")

    briefcase_id: Mapped[int] = mapped_column(ForeignKey("briefcases.id"))
    briefcase: Mapped["BriefcaseModel"] = relationship(lazy="selectin")


class BriefcaseShareModel(Base):
    """Model for BriefcaseShare."""

    __tablename__ = "briefcase_shares"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    created: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    last_updated: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["CompanyModel"] = relationship(lazy="selectin")

    briefcase_id: Mapped[int] = mapped_column(ForeignKey("briefcases.id"))
    briefcase: Mapped["BriefcaseModel"] = relationship(lazy="selectin")

    count: Mapped[int] = mapped_column(nullable=True)
