from .due import Due
from .todoist_base_model import TodoistBaseModel


class Reminder(TodoistBaseModel):
    """Reminder model"""
    notify_uid: str | int | None
    item_id: str | int | None
    type: str
    due: Due | None
    mm_offset: int | None
    name: str | None
    loc_lat: str | None
    loc_long: str | None
    loc_trigger: str | None
    radius: int | None

    class Config:
        """Config for Reminder model"""
        cache_label: str = 'reminders'
        todoist_name: str = 'reminder'
        todoist_resource_type: str = 'reminders'
        command_add: str = 'reminder_add'
