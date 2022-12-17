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
