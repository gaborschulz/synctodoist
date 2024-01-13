from pydantic import ConfigDict, Field

from .due import Due
from .enums import LocTriggerEnum, ReminderTypeEnum
from .todoist_base_model import TodoistBaseModel


class Reminder(TodoistBaseModel):
    """Reminder model"""
    notify_uid: str | int | None = None
    item_id: str | int | None = None
    type: ReminderTypeEnum
    due: Due | None = None
    minute_offset: int | None = Field(None, alias='mm_offset')
    name: str | None = None
    loc_lat: str | None = None
    loc_long: str | None = None
    loc_trigger: LocTriggerEnum | None = None
    radius: int | None = None
    model_config = ConfigDict(populate_by_name=True)

    class TodoistConfig:
        """Config for Reminder model"""
        allow_population_by_field_name = True
        cache_label: str = 'reminders'
        todoist_name: str = 'reminder'
        todoist_resource_type: str = 'reminders'
        command_add: str = 'reminder_add'
        command_delete: str = 'reminder_delete'
        command_update: str = 'reminder_update'
