# pylint: disable-all
import pytest
from pydantic import ValidationError

from synctodoist.exceptions import TodoistError
from synctodoist.models import Task, Due


def test_add_task_no_due_date(synced_todoist, project_inbox):
    task = Task(content="test_add_task_no_due_date", project_id=project_inbox.id)
    assert task.temp_id
    synced_todoist.add_task(task)
    synced_todoist.commit()
    assert task.id
    synced_todoist.delete_task(task=task)
    synced_todoist.commit()


def test_add_task_with_due_date(synced_todoist, project_inbox):
    task = Task(content="test_add_task_with_due_date", project_id=project_inbox.id, due=Due(string='today'))
    assert task.temp_id
    synced_todoist.add_task(task)
    synced_todoist.commit()
    print(task)
    assert task.id
    synced_todoist.delete_task(task=task)
    synced_todoist.commit()


def test_get_task_str_id(synced_todoist, task_added):
    task = synced_todoist.get_task(task_id=task_added.id)
    assert task.id == task_added.id
    assert task.content


def test_get_task_by_pattern(synced_todoist, task_added):
    task = synced_todoist.find_task_by_pattern(pattern='fixture_task_added')
    assert 'fixture_task_added' in task.content


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


def test_reopen_task_by_model(synced_todoist, task_added):
    task = synced_todoist.get_task(task_id=task_added.id)
    synced_todoist.close_task(task=task)
    synced_todoist.commit()
    synced_todoist.reopen_task(task=task)
    synced_todoist.commit()
    task = synced_todoist.get_task(task_id=task_added.id)
    assert not task.checked


def test_reopen_task_by_id(synced_todoist, task_added):
    synced_todoist.close_task(task_id=task_added.id)
    synced_todoist.commit()
    synced_todoist.reopen_task(task_id=task_added.id)
    synced_todoist.commit()
    task = synced_todoist.get_task(task_id=task_added.id)
    assert not task.checked


def test_reopen_task_by_none(synced_todoist):
    with pytest.raises(TodoistError):
        synced_todoist.reopen_task()


def test_delete_task_by_model(synced_todoist, task_added):
    synced_todoist.delete_task(task_id=task_added.id)
    synced_todoist.commit()
    with pytest.raises(TodoistError):
        synced_todoist.get_task(task_id=task_added.id)


def test_delete_task_by_id(synced_todoist, task_added):
    synced_todoist.delete_task(task=task_added)
    synced_todoist.commit()
    with pytest.raises(TodoistError):
        synced_todoist.get_task(task_id=task_added.id)


def test_delete_task_by_none(synced_todoist):
    with pytest.raises(TodoistError):
        synced_todoist.delete_task()


def test_move_task_to_different_project(synced_todoist, task_added):
    target_project = synced_todoist.find_project_by_pattern('Personal')
    assert task_added.project_id != target_project.id
    synced_todoist.move_task(task=task_added, project=target_project)
    synced_todoist.commit()
    assert task_added.project_id == target_project.id


def test_move_task_to_different_section(synced_todoist, task_added, section_added):
    assert task_added.section_id != section_added.id
    synced_todoist.move_task(task=task_added, section=section_added)
    synced_todoist.commit()
    assert task_added.section_id == section_added.id


def test_move_task_to_different_parent(synced_todoist, task_added, task_added_second):
    assert task_added.parent_id != task_added_second.id
    synced_todoist.move_task(task=task_added, parent=task_added_second)
    synced_todoist.commit()
    assert task_added.parent_id == task_added_second.id


def test_move_task_invalid(synced_todoist, task_added):
    with pytest.raises(TodoistError):
        synced_todoist.move_task(task=task_added)


def test_task_priority_constraint():
    with pytest.raises(ValidationError):
        Task(content='Test', priority=10)


def test_update_task(synced_todoist, task_added):
    modified_task = task_added.copy()
    assert task_added.priority != 4
    modified_task.priority = 4
    synced_todoist.update_task(task_id=task_added, task=modified_task)
    synced_todoist.commit()
    assert task_added.priority == modified_task.priority
