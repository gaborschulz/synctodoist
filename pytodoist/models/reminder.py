from pydantic import BaseModel, Field

from pytodoist.models.due import Due
from pytodoist.models.utils import str_uuid4_factory


class Reminder(BaseModel):
    """Reminder model"""
    id: str | int | None
    notify_uid: str | int | None
    item_id: str | int | None
    type: str
    due: Due | None
    mm_offset: int | None
    name: str | None
    loc_lat: str | None
    loc_long: str | None
    loc_trigger: str | None
    radius: int | None
    is_deleted: bool = False
    temp_id: str | None = Field(default_factory=str_uuid4_factory)
