from pydantic import Field

from .due import Due
from .enums import LocTriggerEnum, ReminderTypeEnum
from .todoist_base_model import TodoistBaseModel


class Reminder(TodoistBaseModel):
    """Reminder model"""
    notify_uid: str | int | None
    item_id: str | int | None
    type: ReminderTypeEnum
    due: Due | None
    minute_offset: int | None = Field(alias='mm_offset')
    name: str | None
    loc_lat: str | None
    loc_long: str | None
    loc_trigger: LocTriggerEnum | None
    radius: int | None

    class Config:
        """Config for Reminder model"""
        allow_population_by_field_name = True
        cache_label: str = 'reminders'
        todoist_name: str = 'reminder'
        todoist_resource_type: str = 'reminders'
        command_add: str = 'reminder_add'
        command_delete: str = 'reminder_delete'
        command_update: str = 'reminder_update'
