# pylint: disable-all
import os

import pytest
from dotenv import load_dotenv

from pytodoist import TodoistAPI
from pytodoist.exceptions import TodoistError
from pytodoist.models import Task, Due

load_dotenv()
API_KEY = os.environ.get('TODOIST_API')
INBOX_ID = ''
TASK_ID = []


@pytest.fixture()
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
    global INBOX_ID
    todoist.sync()
    project = todoist.get_project_by_pattern(pattern='Inbox')
    print(project)
    INBOX_ID = project.id
    assert project.name == 'Inbox'


def test_get_project_by_pattern_synced_notexisting(todoist):
    todoist.sync()
    project = todoist.get_project_by_pattern(pattern='NON_EXISTING_PROJECT')
    assert project is None


def test_get_stats(todoist):
    stats = todoist.get_stats()
    assert 'karma' in stats


def test_add_task_no_due_date(todoist):
    global TASK_ID
    task = Task(content="Buy Raspberries", project_id=INBOX_ID)
    assert task.temp_id
    todoist.add_task(task)
    todoist.commit()
    print(task)
    TASK_ID.append(task.id)
    assert task.id


def test_add_task_with_due_date(todoist):
    global TASK_ID
    task = Task(content="Buy Honey", project_id=INBOX_ID, due=Due(string='today'))
    assert task.temp_id
    todoist.add_task(task)
    todoist.commit()
    print(task)
    TASK_ID.append(task.id)
    assert task.id


def test_get_task_str_id(todoist):
    task = todoist.get_task(task_id=str(TASK_ID[0]))
    assert task.id == str(TASK_ID[0])
    assert task.content


def test_get_task_int_id(todoist):
    task = todoist.get_task(task_id=int(TASK_ID[0]))
    assert task.id == str(TASK_ID[0])
    assert task.content


def test_close_task_nothing_provided(todoist):
    with pytest.raises(TodoistError):
        todoist.close_task()


def test_close_task_by_model(todoist):
    task_id = TASK_ID.pop()
    task = todoist.get_task(task_id=task_id)
    todoist.close_task(task=task)
    todoist.commit()
    task = todoist.get_task(task_id=task_id)
    assert task.checked


def test_close_task_by_id(todoist):
    task_id = TASK_ID.pop()
    todoist.close_task(task_id=task_id)
    todoist.commit()
    task = todoist.get_task(task_id=task_id)
    assert task.checked


def test_close_task_uncommitted(todoist):
    task = Task(content='Buy Groceries', project_id=INBOX_ID)
    todoist.add_task(task=task)
    todoist.close_task(task=task)
    todoist.commit()
