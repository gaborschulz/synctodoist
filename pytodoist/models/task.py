from datetime import datetime

from pydantic import BaseModel, Field

from .due import Due
from .utils import str_uuid4_factory


class Task(BaseModel):
    """Task model"""
    id: str | None
    user_id: str | int | None
    project_id: str | int | None
    content: str | None
    description: str | None
    priority: int | None
    due: Due | None
    parent_id: str | int | None
    child_order: int | None
    section_id: str | int | None
    day_order: int | None
    collapsed: bool | None
    labels: list[str] | None
    added_by_uid: str | int | None
    assigned_by_uid: str | int | None
    responsible_uid: str | int | None
    checked: bool | None
    is_deleted: bool | None
    sync_id: str | int | None
    added_at: datetime | None
    temp_id: str | None = Field(default_factory=str_uuid4_factory)
