from datetime import datetime, date
from typing import Annotated

from pydantic import BaseModel, Field


class Due(BaseModel):
    """Due model"""
    date: Annotated[date | datetime | None, Field(default=None)]
    is_recurring: bool = False
    lang: str | None = None
    string: str | None = None
    timezone: str | None = None
