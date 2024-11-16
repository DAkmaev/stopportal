from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

from backend.app.db.models.company import CompanyModel


class TADecisionModel(SQLModel, table=True):
    __tablename__ = "stoch_decisions"

    id: int = Field(primary_key=True, default=None)
    period: str = Field(nullable=False, index=True)
    decision: str = Field(nullable=False)
    k: float = Field(nullable=True)  # noqa: WPS111
    d: float = Field(nullable=True)  # noqa: WPS111
    last_price: float = Field(nullable=True)

    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    company_id: int = Field(foreign_key="companies.id")
    company: CompanyModel = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
