# pylint: disable-all
import pytest

from synctodoist.exceptions import TodoistError
from synctodoist.models import ColorEnum


def test_get_project_str_id(todoist, project_added):
    project_id = project_added.id
    project = todoist.get_project(project_id=project_id)
    assert project.name == project_added.name


def test_get_project_int_id(todoist, project_added):
    project_id = int(project_added.id)
    project = todoist.get_project(project_id=project_id)
    assert project.name == project_added.name


def test_get_project_by_pattern_synced_existing(synced_todoist, project_inbox):
    assert project_inbox.name == 'Inbox'


def test_get_project_by_pattern_synced_non_existing(synced_todoist):
    with pytest.raises(TodoistError):
        synced_todoist.find_project(pattern='NON_EXISTING_PROJECT')


def test_add_project(project_added):
    assert project_added.id


def test_delete_project_by_model(synced_todoist, project_added):
    synced_todoist.delete_project(project=project_added)
    synced_todoist.commit()
    with pytest.raises(TodoistError):
        synced_todoist.get_project(project_id=project_added.id)


def test_delete_project_by_id(synced_todoist, project_added):
    synced_todoist.delete_project(project_id=project_added.id)
    synced_todoist.commit()
    with pytest.raises(TodoistError):
        synced_todoist.get_project(project_id=project_added.id)


def test_delete_project_by_none(synced_todoist):
    with pytest.raises(TodoistError):
        synced_todoist.delete_project()


def test_update_project(synced_todoist, project_added):
    modified_project = project_added.copy()
    modified_project.color = ColorEnum.mint_green
    synced_todoist.update_project(project_id=project_added, project=modified_project)
    synced_todoist.commit()
    assert project_added.color == modified_project.color
