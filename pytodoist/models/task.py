from datetime import datetime

from pydantic import BaseModel

from .due import Due


class Task(BaseModel):
    """Task model"""
    id: str | None
    user_id: str | int
    project_id: str | int
    content: str
    description: str
    priority: int
    due: Due | None
    parent_id: str | int | None
    child_order: int
    section_id: str | int | None
    day_order: int | None
    collapsed: bool
    labels: list[str]
    added_by_uid: str | int
    assigned_by_uid: str | int | None
    responsible_uid: str | int | None
    checked: bool
    is_deleted: bool
    sync_id: str | int | None
    added_at: datetime | None
    temp_id: str | None
