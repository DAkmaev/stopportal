from datetime import datetime

from pydantic import BaseModel


class Dummy(BaseModel):
    id: str
    status: str
