from datetime import datetime

from pydantic import BaseModel


class CronJobRunDTO(BaseModel):
    id: int
    name: str
    period: str
    last_run_date: datetime


class CronJobRunInputDTO(BaseModel):
    name: str
    period: str
