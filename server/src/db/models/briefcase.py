import enum
from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel, Enum, Column
from src.db.models.company import CompanyModel, StrategyModel
from src.db.models.user import UserModel


class CurrencyEnum(enum.Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class RegistryOperationEnum(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDENDS = "DIVIDENDS"


class BriefcaseModel(SQLModel, table=True):
    """Model for Briefcase."""

    __tablename__ = "briefcases"

    id: int = Field(primary_key=True, default=None)
    fill_up: Decimal | None = Field(nullable=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    user: UserModel = Relationship()


class BriefcaseRegistryModel(SQLModel, table=True):
    """Model for BriefcaseRegistryItem."""

    __tablename__ = "briefcase_registry"

    id: int = Field(primary_key=True, default=None)
    created_date: datetime = Field()
    currency: CurrencyEnum = Field(sa_column=Column(Enum(CurrencyEnum), default=CurrencyEnum.RUB))
    operation: RegistryOperationEnum = Field(sa_column=Column(Enum(RegistryOperationEnum)))
    count: int | None = Field(nullable=True)
    amount: Decimal = Field(nullable=True)  # Сумма сделки
    price: Decimal | None = Field(nullable=True)

    company_id: int = Field(foreign_key="companies.id")
    company: CompanyModel = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    strategy_id: int = Field(foreign_key="strategies.id", nullable=True)
    strategy: StrategyModel = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    briefcase_id: int = Field(foreign_key="briefcases.id")
    briefcase: BriefcaseModel = Relationship(sa_relationship_kwargs={"lazy": "selectin"})


class BriefcaseShareModel(SQLModel, table=True):
    """Model for BriefcaseShare."""

    __tablename__ = "briefcase_shares"
    id: int = Field(primary_key=True, default=None)

    created: datetime = Field()
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    company_id: int = Field(foreign_key="companies.id")
    company: CompanyModel = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    briefcase_id: int = Field(foreign_key="briefcases.id")
    briefcase: BriefcaseModel = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    count: int = Field(nullable=True)
