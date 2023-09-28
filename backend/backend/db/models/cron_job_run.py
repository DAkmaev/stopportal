import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, DateTime

from backend.db.base import Base

if TYPE_CHECKING:
    from .item import Item  # noqa: F401


class CronJobRunModel(Base):
    __tablename__ = "cron_job_run"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    last_run_date: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime)
