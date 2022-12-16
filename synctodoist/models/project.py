from .todoist_base_model import TodoistBaseModel


class Project(TodoistBaseModel):
    """Project model"""
    name: str
    color: str
    parent_id: str | int | None
    child_order: int | None
    collapsed: bool = False
    shared: bool = False
    sync_id: str | int | None
    is_archived: bool = False
    is_favorite: bool = False
    view_style: str | None

    cache_label: str = 'projects'
    todoist_name: str = 'project'
    todoist_field_name: str = 'projects'
