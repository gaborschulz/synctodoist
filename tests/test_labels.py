# pylint: disable-all
import pytest

from synctodoist.exceptions import TodoistError


def test_get_label_int_id(synced_todoist, label_added):
    label = synced_todoist.get_label(label_id=int(label_added.id))
    assert label.name == label_added.name


def test_get_label_str_id(synced_todoist, label_added):
    label = synced_todoist.get_label(label_id=str(label_added.id))
    assert label.name == label_added.name


def test_get_label_by_pattern(synced_todoist, label_added):
    label = synced_todoist.get_label_by_pattern(pattern='test')
    assert 'test' in label.name


def test_get_label_unsynced(todoist, label_added):
    with pytest.raises(TodoistError):
        todoist.get_label(label_id=label_added.id)


def test_delete_label_by_model(synced_todoist, label_added):
    synced_todoist.delete_label(label=label_added)
    synced_todoist.commit()
    with pytest.raises(TodoistError):
        synced_todoist.get_label(label_id=label_added.id)


def test_delete_label_by_id(synced_todoist, label_added):
    synced_todoist.delete_label(label_id=label_added.id)
    synced_todoist.commit()
    with pytest.raises(TodoistError):
        synced_todoist.get_label(label_id=label_added.id)
