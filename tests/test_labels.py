# pylint: disable-all
import pytest

from synctodoist.exceptions import TodoistError
from synctodoist.models import ColorEnum


def test_get_label_int_id(synced_todoist, label_added):
    label = synced_todoist.get_label(label_id=int(label_added.id))
    assert label.name == label_added.name


def test_get_label_str_id(synced_todoist, label_added):
    label = synced_todoist.get_label(label_id=str(label_added.id))
    assert label.name == label_added.name


def test_get_label_by_pattern(synced_todoist, label_added):
    label = synced_todoist.find_label_by_pattern(pattern='fixture_label_added')
    assert 'fixture_label_added' in label.name


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


def test_delete_label_by_none(synced_todoist):
    with pytest.raises(TodoistError):
        synced_todoist.delete_label()


def test_update_label(synced_todoist, label_added):
    modified_label = label_added.copy()
    modified_label.color = ColorEnum.mint_green
    synced_todoist.update_label(label_id=label_added, label=modified_label)
    synced_todoist.commit()
    assert label_added.color == modified_label.color
