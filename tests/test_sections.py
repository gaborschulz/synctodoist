# pylint: disable-all
from datetime import datetime

import pytest

from synctodoist.exceptions import TodoistError


def test_get_section_int_id(synced_todoist, section_added):
    section = synced_todoist.get_section(section_id=int(section_added.id))
    assert section.name == section_added.name


def test_get_section_str_id(synced_todoist, section_added):
    section = synced_todoist.get_section(section_id=str(section_added.id))
    assert section.name == section_added.name


def test_get_section_by_pattern(synced_todoist, section_added):
    section = synced_todoist.find_section_by_pattern(pattern='fixture_section_added')
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


def test_delete_section_by_none(synced_todoist):
    with pytest.raises(TodoistError):
        synced_todoist.delete_section()


def test_update_section(synced_todoist, section_added):
    modified_section = section_added.copy()
    modified_section.name = f'test_update_section_{int(datetime.now().timestamp())}'
    synced_todoist.update_section(section_id=section_added, section=modified_section)
    synced_todoist.commit()
    assert section_added.name == modified_section.name
