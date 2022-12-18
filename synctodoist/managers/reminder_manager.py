from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Reminder


class ReminderManager(BaseManager[Reminder]):
    """Reminder manager"""
    model = Reminder
