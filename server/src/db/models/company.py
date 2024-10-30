from sqlmodel import Field, SQLModel, Relationship

from server.src.db.models.user import UserModel


class CompanyStrategy(SQLModel, table=True):
    __tablename__ = 'companies_strategies'

    company_id: int | None = Field(default=None, foreign_key="companies.id", primary_key=True)
    strategy_id: int | None = Field(default=None, foreign_key="strategies.id", primary_key=True)


class CompanyModel(SQLModel, table=True):
    __tablename__ = "companies"

    id: int = Field(primary_key=True, default=None)
    name: str = Field(index=True, unique=True, nullable=True)
    tiker: str = Field(index=True, unique=True)
    type: str = Field(default="MOEX", nullable=True)
    stops: list["StopModel"] = Relationship(sa_relationship_kwargs={"lazy": "selectin"}, cascade_delete=True)

    strategies: list["StrategyModel"] = Relationship(
        back_populates="companies",
        link_model=CompanyStrategy,
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    user_id: int = Field(foreign_key="user.id", index=True)
    user: UserModel = Relationship()


class StopModel(SQLModel, table=True):
    __tablename__ = "companies_stop"

    id: int = Field(primary_key=True, default=None)
    period: str = Field()
    value: float = Field(nullable=False)
    company_id: int = Field(foreign_key="companies.id")


class StrategyModel(SQLModel, table=True):
    __tablename__ = "strategies"

    id: int = Field(primary_key=True, default=None)
    name: str = Field(index=True, unique=True, nullable=False)
    description: str = Field(nullable=True)

    companies: list["CompanyModel"] = Relationship(
        back_populates="strategies",
        link_model=CompanyStrategy
    )

    user_id: int = Field(foreign_key="user.id", index=True)
    user: UserModel = Relationship()
