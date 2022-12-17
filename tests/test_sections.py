# pylint: disable-all
import pytest

from synctodoist.exceptions import TodoistError


def test_get_section_int_id(synced_todoist, section_added):
    section = synced_todoist.get_section(section_id=int(section_added.id))
    assert section.name == section_added.name


def test_get_section_str_id(synced_todoist, section_added):
    section = synced_todoist.get_section(section_id=str(section_added.id))
    assert section.name == section_added.name


def test_get_section_by_pattern(synced_todoist, section_added):
    section = synced_todoist.get_section_by_pattern(pattern='fixture_section_added')
    assert section.name == section_added.name


def test_get_section_unsynced(todoist, section_added):
    with pytest.raises(TodoistError):
        todoist.get_section(section_id=section_added.id)


def test_delete_section_by_model(synced_todoist, section_added):
    synced_todoist.delete_section(section=section_added)
    synced_todoist.commit()
    with pytest.raises(TodoistError):
        synced_todoist.get_section(section_id=section_added.id)


def test_delete_section_by_id(synced_todoist, section_added):
    synced_todoist.delete_section(section_id=section_added.id)
    synced_todoist.commit()
    with pytest.raises(TodoistError):
        synced_todoist.get_section(section_id=section_added.id)
