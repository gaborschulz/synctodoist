from .todoist_base_model import TodoistBaseModel


class Label(TodoistBaseModel):
    """Label model"""
    name: str
    color: str | None
    item_order: int | None
    is_favorite: bool = False

    cache_label: str = 'labels'
    todoist_name: str = 'label'
    todoist_field_name: str = 'labels'
