from datetime import datetime

from pydantic import ConfigDict

from .todoist_base_model import TodoistBaseModel


class Section(TodoistBaseModel):
    """Section model"""
    name: str
    project_id: str | int
    section_order: int | None = None
    collapsed: bool = False
    user_id: str | int | None = None
    sync_id: str | int | None = None
    is_archived: bool = False
    archived_at: datetime | None = None
    added_at: datetime | None = None
    model_config = ConfigDict()

    class TodoistConfig:
        """Config for Section model"""
        cache_label: str = 'sections'
        todoist_name: str = 'section'
        todoist_resource_type: str = 'sections'
        command_add: str = 'section_add'
        command_delete: str = 'section_delete'
        command_update: str = 'section_update'
