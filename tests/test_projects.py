# pylint: disable-all
import pytest

from synctodoist.exceptions import TodoistError


def test_get_project_str_id(todoist):
    project_id = '2303492502'
    project = todoist.get_project(project_id=project_id)
    assert project.name == 'Inbox'


def test_get_project_int_id(todoist):
    project_id = 2303492502
    project = todoist.get_project(project_id=project_id)
    assert project.name == 'Inbox'


def test_get_project_by_pattern_unsynced(todoist):
    with pytest.raises(TodoistError):
        todoist.get_project_by_pattern(pattern='Inbox')


def test_get_project_by_pattern_synced_existing(synced_todoist, project_inbox):
    assert project_inbox.name == 'Inbox'


def test_get_project_by_pattern_synced_non_existing(synced_todoist):
    with pytest.raises(TodoistError):
        synced_todoist.get_project_by_pattern(pattern='NON_EXISTING_PROJECT')


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
