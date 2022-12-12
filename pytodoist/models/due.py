from datetime import datetime, date

from pydantic import BaseModel


class Due(BaseModel):
    """Due model"""
    date: datetime | date | None
    is_recurring: bool = False
    lang: str | None
    string: str | None
    timezone: str | None
