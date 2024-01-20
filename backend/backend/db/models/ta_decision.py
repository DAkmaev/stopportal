from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String, Float, TIMESTAMP

from backend.db.base import Base


class TADecisionModel(Base):
    __tablename__ = "stoch_decisions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period: Mapped[str] = mapped_column(String, nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String, nullable=False)
    k: Mapped[float] = mapped_column(Float, nullable=True)
    d: Mapped[float] = mapped_column(Float, nullable=True)
    last_price: Mapped[float] = mapped_column(Float, nullable=True)
    last_updated: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    company: Mapped["CompanyModel"] = relationship(lazy="selectin")
