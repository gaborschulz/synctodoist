from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Reminder


class ReminderManager(BaseManager[Reminder]):
    """Reminder manager"""
    model = Reminder

    def delete(self, reminder_id: int | str | None = None, *, reminder: Reminder | None = None) -> None:
        """Delete a reminder

        Args:
            reminder_id: the id of the reminder to delete
            reminder: the Reminder object to delete (keyword-only argument)

        Either the reminder_id or the reminder must be provided. The reminder object takes priority over the reminder_id argument if both are provided
        """

        if not reminder_id and not reminder:
            raise TodoistError('Either reminder_id or reminder have to be provided')

        if isinstance(reminder, Reminder):
            if not reminder.id:
                reminder_id = reminder.temp_id
            else:
                reminder_id = str(reminder.id)

        if isinstance(reminder_id, int):
            reminder_id = str(reminder_id)

        command_manager.add_command(data={'id': reminder_id}, command_type='reminder_delete')
