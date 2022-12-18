# pylint: disable-all
import pytest

from synctodoist.exceptions import TodoistError


def test_add_reminder(synced_todoist, reminder_added):
    assert reminder_added.id


def test_delete_reminder_by_model(synced_todoist, reminder_added):
    synced_todoist.delete_reminder(reminder=reminder_added)
    synced_todoist.commit()
    with pytest.raises(TodoistError):
        synced_todoist.get_reminder(reminder_id=reminder_added.id)


def test_delete_reminder_by_id(synced_todoist, reminder_added):
    synced_todoist.delete_reminder(reminder_id=reminder_added.id)
    synced_todoist.commit()
    with pytest.raises(TodoistError):
        synced_todoist.get_reminder(reminder_id=reminder_added.id)


@pytest.mark.skip(reason='Only runs in paid Todoist account')
def test_update_reminder(synced_todoist, reminder_added):
    modified_reminder = reminder_added.copy()
    modified_reminder.minute_offset = 60
    synced_todoist.update_reminder(reminder_id=reminder_added, reminder=modified_reminder)
    synced_todoist.commit()
    assert reminder_added.minute_offset == modified_reminder.minute_offset
