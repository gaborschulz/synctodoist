# pylint: disable-all
from datetime import datetime
from random import randint

import pytest

from synctodoist import TodoistAPI
from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.models import Task, Due, Project, Label, Section, Reminder, ReminderTypeEnum, Settings


@pytest.fixture()
def todoist():
    settings = Settings(_env_file='.env', timeout=30)
    todoist = TodoistAPI(settings=settings)
    return todoist


@pytest.fixture(scope='session')
def synced_todoist():
    settings = Settings(_env_file='.env', timeout=30)
    todoist = TodoistAPI(settings=settings)
    todoist.sync()
    return todoist


@pytest.fixture(scope='session')
def project_inbox(synced_todoist):
    return synced_todoist.find_project('Inbox')


@pytest.fixture
def task_added(synced_todoist, project_inbox):
    task = Task(content=f'fixture_task_added ({datetime.now().isoformat()})', project_id=project_inbox.id, due=Due(string='today 18:00'))
    synced_todoist.add_task(task)
    synced_todoist.commit()
    yield task
    try:
        synced_todoist.delete_task(task=task)
        synced_todoist.commit()
    except TodoistError as ex:
        print(ex)


task_added_second = task_added


@pytest.fixture
def project_added(synced_todoist):
    project = Project(name=f'fixture_project_added_{int(datetime.now().timestamp())}_{randint(0, 10000)}')
    synced_todoist.add_project(project)
    synced_todoist.commit()
    yield project
    synced_todoist.delete_project(project=project)
    synced_todoist.commit()


@pytest.fixture
def label_added(synced_todoist):
    label = Label(name=f'fixture_label_added_{int(datetime.now().timestamp())}_{randint(0, 10000)}')
    synced_todoist.add_label(label)
    synced_todoist.commit()
    yield label
    synced_todoist.delete_label(label=label)
    synced_todoist.commit()


@pytest.fixture
def section_added(synced_todoist, project_added):
    section = Section(name=f'fixture_section_added_{int(datetime.now().timestamp())}_{randint(0, 10000)}', project_id=project_added.id)
    synced_todoist.add_section(section)
    synced_todoist.commit()
    yield section
    try:
        synced_todoist.delete_section(section=section)
        synced_todoist.commit()
    except TodoistError as ex:
        print(ex)


@pytest.fixture
def reminder_added(synced_todoist, task_added):
    reminder = Reminder(item_id=task_added.id, type=ReminderTypeEnum.relative, minute_offset=30)
    synced_todoist.add_reminder(reminder)
    synced_todoist.commit()
    yield reminder


@pytest.fixture(autouse=True, scope='session')
def print_total_todoist_count():
    # setup_stuff
    yield
    print('\n\n')
    print('Todoist Call Summary')
    print('-' * 30)
    print(f'{command_manager.full_sync_count = }')
    print(f'{command_manager.partial_sync_count = }')
    print('-' * 30)
