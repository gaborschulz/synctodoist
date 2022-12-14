# pylint: disable-all
import os

import pytest
from dotenv import load_dotenv

from pytodoist import TodoistAPI
from pytodoist.exceptions import TodoistError
from pytodoist.models import Task, Due

load_dotenv()
API_KEY = os.environ.get('TODOIST_API')


@pytest.fixture()
def todoist():
    todoist = TodoistAPI(api_key=API_KEY)
    return todoist


@pytest.fixture(scope='session')
def synced_todoist():
    todoist = TodoistAPI(api_key=API_KEY)
    todoist.sync()
    return todoist


@pytest.fixture(scope='session')
def project_inbox(synced_todoist):
    return synced_todoist.get_project_by_pattern('Inbox')


@pytest.fixture
def task_added(synced_todoist, project_inbox):
    task_added = Task(content="Buy Raspberries", project_id=project_inbox.id)
    synced_todoist.add_task(task_added)
    synced_todoist.commit()
    return task_added


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


def test_get_project_by_pattern_synced_existing(synced_todoist, project_inbox):
    print(project_inbox)
    assert project_inbox.name == 'Inbox'


def test_get_project_by_pattern_synced_notexisting(synced_todoist):
    project = synced_todoist.get_project_by_pattern(pattern='NON_EXISTING_PROJECT')
    assert project is None


def test_get_stats(todoist):
    stats = todoist.get_stats()
    assert 'karma' in stats


def test_add_task_no_due_date(synced_todoist, project_inbox):
    task = Task(content="Buy Raspberries", project_id=project_inbox.id)
    assert task.temp_id
    synced_todoist.add_task(task)
    synced_todoist.commit()
    print(task)
    assert task.id


def test_add_task_with_due_date(synced_todoist, project_inbox):
    task = Task(content="Buy Honey", project_id=project_inbox.id, due=Due(string='today'))
    assert task.temp_id
    synced_todoist.add_task(task)
    synced_todoist.commit()
    print(task)
    assert task.id


def test_get_task_str_id(synced_todoist, task_added):
    task = synced_todoist.get_task(task_id=task_added.id)
    assert task.id == task_added.id
    assert task.content


def test_get_task_int_id(synced_todoist, task_added):
    task = synced_todoist.get_task(task_id=int(task_added.id))
    assert task.id == task_added.id
    assert task.content


def test_close_task_nothing_provided(todoist):
    with pytest.raises(TodoistError):
        todoist.close_task()


def test_close_task_by_model(synced_todoist, task_added):
    task = synced_todoist.get_task(task_id=task_added.id)
    synced_todoist.close_task(task=task)
    synced_todoist.commit()
    task = synced_todoist.get_task(task_id=task_added.id)
    assert task.checked


def test_close_task_by_id(synced_todoist, task_added):
    synced_todoist.close_task(task_id=task_added.id)
    synced_todoist.commit()
    task = synced_todoist.get_task(task_id=task_added.id)
    assert task.checked


def test_close_task_uncommitted(synced_todoist, project_inbox):
    task = Task(content='Buy Groceries', project_id=project_inbox.id)
    synced_todoist.add_task(task=task)
    synced_todoist.close_task(task=task)
    synced_todoist.commit()
    task = synced_todoist.get_task(task_id=task.id)
    assert task.checked
