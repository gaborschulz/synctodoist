from datetime import datetime

from pydantic import BaseModel, Field

from pytodoist.models.utils import str_uuid4_factory


class Section(BaseModel):
    """Section model"""
    id: str | int | None
    name: str
    project_id: str | int
    section_order: int | None
    collapsed: bool = False
    user_id: str | int | None
    sync_id: str | int | None
    is_deleted: bool = False
    is_archived: bool = False
    archived_at: datetime | None
    added_at: datetime | None
    temp_id: str | None = Field(default_factory=str_uuid4_factory)
