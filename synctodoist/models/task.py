from datetime import datetime

from pydantic import conint

from .due import Due
from .todoist_base_model import TodoistBaseModel


class Task(TodoistBaseModel):
    """Task model"""
    user_id: str | int | None
    project_id: str | int | None
    content: str | None
    description: str | None
    priority: conint(ge=1, le=4) | None  # type: ignore
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
    auto_reminder: bool = False

    class Config:
        """Config for Task model"""
        cache_label: str = 'tasks'
        todoist_name: str = 'item'
        todoist_resource_type: str = 'items'
        command_add: str = 'item_add'
        command_delete: str = 'item_delete'
        command_close: str = 'item_complete'
        command_reopen: str = 'item_uncomplete'
        command_move: str = 'item_move'
        command_update: str = 'item_update'
        api_get: str = 'items/get'
