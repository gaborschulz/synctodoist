# pylint: disable-all
import os

import pytest
from dotenv import load_dotenv

from pytodoist import TodoistAPI
from pytodoist.exceptions import TodoistError

load_dotenv()
API_KEY = os.environ.get('TODOIST_API')


@pytest.fixture
def todoist():
    todoist = TodoistAPI(api_key=API_KEY)
    return todoist


def test_init(todoist):
    assert todoist._api_key == API_KEY
    assert 'Authorization' in todoist._headers
    assert 'Content-Type' in todoist._headers


def test_sync(todoist):
    assert not todoist.synced
    todoist.sync()
    assert todoist.synced
    assert len(todoist.projects) > 0


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


def test_get_project_by_pattern_synced_existing(todoist):
    todoist.sync()
    project = todoist.get_project_by_pattern(pattern='Inbox')
    assert project.name == 'Inbox'


def test_get_project_by_pattern_synced_notexisting(todoist):
    todoist.sync()
    project = todoist.get_project_by_pattern(pattern='NON_EXISTING_PROJECT')
    assert project is None
