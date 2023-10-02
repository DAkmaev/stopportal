from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, Boolean

from backend.db.base import Base

if TYPE_CHECKING:
    from .item import Item  # noqa: F401


class StockModel(Base):
    __tablename__ = "stock"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tiker: Mapped[str] = mapped_column(String, index=True, unique=True)
    type: Mapped[str] = mapped_column(String, default='MOEX', nullable=True)
