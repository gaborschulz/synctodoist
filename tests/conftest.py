# pylint: disable-all
import os
from datetime import datetime
from random import randint

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
    task = Task(content=f'fixutre_task_added ({datetime.now().isoformat()})', project_id=project_inbox.id, due=Due(string='today 18:00'))
    synced_todoist.add_task(task)
    synced_todoist.commit()
    yield task
    synced_todoist.delete_task(task=task)


@pytest.fixture
def project_added(synced_todoist):
    project = Project(name=f'test_{int(datetime.now().timestamp())}_{randint(0, 10000)}')
    synced_todoist.add_project(project)
    synced_todoist.commit()
    yield project
    synced_todoist.delete_project(project=project)


@pytest.fixture
def label_added(synced_todoist):
    label = Label(name=f'test_{int(datetime.now().timestamp())}_{randint(0, 10000)}')
    synced_todoist.add_label(label)
    synced_todoist.commit()
    yield label
    synced_todoist.delete_label(label=label)
