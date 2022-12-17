# pylint: disable-all
import os
from datetime import datetime

import pytest
from dotenv import load_dotenv

from synctodoist import TodoistAPI
from synctodoist.models import Task, Due, Project

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
    return task_added


@pytest.fixture
def project_added(synced_todoist):
    project = Project(name='test')
    synced_todoist.add_project(project)
    synced_todoist.commit()
    return project
