from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class Account(BaseModel):
    id: str
    balance: float = 0
    status: str = "active"
    state: dict = {}
    work_now: bool = False
    last_game: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        from_attributes = True
