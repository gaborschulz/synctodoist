# pylint: disable-all
from synctodoist.models import Reminder


def test_add_reminder(synced_todoist, task_added):
    reminder = Reminder(item_id=task_added.id, type='relative', mm_offset=30)
    synced_todoist.add_reminder(reminder)
    synced_todoist.commit()
    assert reminder.id
