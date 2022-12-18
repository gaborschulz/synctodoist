from .enums import ColorEnum
from .todoist_base_model import TodoistBaseModel


class Label(TodoistBaseModel):
    """Label model"""
    name: str
    color: ColorEnum | None
    item_order: int | None
    is_favorite: bool = False

    class Config:
        """Config for Label model"""
        cache_label: str = 'labels'
        todoist_name: str = 'label'
        todoist_resource_type: str = 'labels'
        command_add: str = 'label_add'
        command_delete: str = 'label_delete'
        command_update: str = 'label_update'
