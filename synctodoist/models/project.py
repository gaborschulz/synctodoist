from .enums import ColorEnum
from .todoist_base_model import TodoistBaseModel


class Project(TodoistBaseModel):
    """Project model"""
    name: str
    color: ColorEnum | None
    parent_id: str | int | None
    child_order: int | None
    collapsed: bool = False
    shared: bool = False
    sync_id: str | int | None
    is_archived: bool = False
    is_favorite: bool = False
    view_style: str | None

    class Config:
        """Config for Project model"""
        cache_label: str = 'projects'
        todoist_name: str = 'project'
        todoist_resource_type: str = 'projects'
        command_add: str = 'project_add'
        command_delete: str = 'project_delete'
        command_update: str = 'project_update'
        api_get: str = 'projects/get'
