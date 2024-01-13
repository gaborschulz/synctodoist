from datetime import datetime

from pydantic import Field, ConfigDict
from typing_extensions import Annotated

from .due import Due
from .todoist_base_model import TodoistBaseModel


class Task(TodoistBaseModel):
    """Task model"""
    user_id: str | int | None = None
    project_id: str | int | None = None
    content: str | None = None
    description: str | None = None
    priority: Annotated[int, Field(ge=1, le=4)] | None = None  # type: ignore
    due: Due | None = None
    parent_id: str | int | None = None
    child_order: int | None = None
    section_id: str | int | None = None
    day_order: int | None = None
    collapsed: bool | None = None
    labels: list[str] | None = None
    added_by_uid: str | int | None = None
    assigned_by_uid: str | int | None = None
    responsible_uid: str | int | None = None
    checked: bool | None = None
    sync_id: str | int | None = None
    added_at: datetime | None = None
    auto_reminder: bool = False
    model_config = ConfigDict()

    class TodoistConfig:
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
