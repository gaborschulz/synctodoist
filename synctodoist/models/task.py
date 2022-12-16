from datetime import datetime

from .due import Due
from .todoist_base_model import TodoistBaseModel


class Task(TodoistBaseModel):
    """Task model"""
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
    sync_id: str | int | None
    added_at: datetime | None

    cache_label: str = 'tasks'
    todoist_name: str = 'item'
    todoist_field_name: str = 'items'