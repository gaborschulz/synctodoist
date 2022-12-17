# pylint: disable-all
import os
from datetime import datetime

import pytest
from dotenv import load_dotenv

from synctodoist import TodoistAPI
from synctodoist.models import Task, Due, Project, Label

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
    task_added = Task(content=f'Buy Raspberries ({datetime.now().isoformat()})', project_id=project_inbox.id, due=Due(string='today 18:00'))
    synced_todoist.add_task(task_added)
    synced_todoist.commit()
    yield task_added
    synced_todoist.delete_task(task=task_added)


@pytest.fixture
def project_added(synced_todoist):
    project = Project(name=f'test {int(datetime.now().timestamp())}')
    synced_todoist.add_project(project)
    synced_todoist.commit()
    yield project
    synced_todoist.delete_project(project=project)


@pytest.fixture
def label_added(synced_todoist):
    label = Label(name=f'test_{int(datetime.now().timestamp())}')
    synced_todoist.add_label(label)
    synced_todoist.commit()
    yield label
