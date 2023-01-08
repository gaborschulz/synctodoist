from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Reminder


class ReminderManager(BaseManager[Reminder]):
    """Reminder manager"""
    model = Reminder

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, model=Reminder, **kwargs)
