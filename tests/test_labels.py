# pylint: disable-all
import pytest

from synctodoist.exceptions import TodoistError


def test_get_label_int_id(synced_todoist, label_added):
    label = synced_todoist.get_label(label_id=int(label_added.id))
    assert label.name == label_added.name


def test_get_label_str_id(synced_todoist, label_added):
    label = synced_todoist.get_label(label_id=str(label_added.id))
    assert label.name == label_added.name


def get_label_unsynced(todoist, label_added):
    with pytest.raises(TodoistError):
        todoist.get_label(label_id=label_added.id)
