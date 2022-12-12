import inspect
import json
import re
import uuid
from typing import Any

import httpx

from pytodoist.models import Task, Project, Due, Command

BASE_URL = 'https://api.todoist.com/sync/v9'
APIS = {
    'sync': 'sync',
    'get_task': 'items/get',
    'get_stats': 'completed/get_stats',
    'get_project': 'projects/get',
    'commit': 'sync',
}


class TodoistAPI:  # pylint: disable=too-few-public-methods
    """Todoist API class for the new Sync v9 API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self._sync_token: str = '*'
        self.projects: list = []
        self._commands: dict[str, Command] = {}
        self._temp_tasks: dict[str, Task] = {}

    def sync(self) -> Any:
        """Synchronize with Todoist API

        Returns:
            A dict with all projects
        """
        method_name = inspect.stack()[0][3]
        data = {'resource_types': ['projects']}
        result = self._post(data, method_name)
        self.projects = [Project(**x) for x in result['projects']]
        return result

    def get_task(self, task_id: int | str) -> Any:
        """Get task by id

        Args:
            task_id: the id of the task

        Returns:
            A dict with all task details
        """
        method_name = inspect.stack()[0][3]
        if isinstance(task_id, str):
            task_id = int(task_id)

        data = {'item_id': task_id}
        result = self._post(data, method_name)
        task = Task(**result.get('item'))
        return task

    def get_project(self, project_id: int | str) -> Any:
        """Get project by name

        Args:
            project_id: the id of the project

        Returns:
            A dict with all project details
        """
        method_name = inspect.stack()[0][3]
        if isinstance(project_id, str):
            project_id = int(project_id)

        data = {'project_id': project_id, 'all_data': False}
        result = self._post(data, method_name)
        project = Project(**result['project'])
        return project

    def get_project_by_pattern(self, pattern: str) -> Any:
        """Get a project if its name matches a regex pattern

        Args:
            pattern: the regex pattern against which the project's name is matched

        Returns:
            A dict containing the project details
        """
        compiled_pattern = re.compile(pattern=pattern)
        for project in self.projects:
            if compiled_pattern.findall(project.name):
                return project

        return None

    def get_stats(self) -> dict:
        """Get Todoist usage statistics

        Returns:
            A dict with all user stats
        """
        method_name = inspect.stack()[0][3]
        url = f'{BASE_URL}/{APIS[method_name]}'
        with httpx.Client(headers=self.headers) as client:
            response = client.get(url=url)
            response.raise_for_status()
            return response.json()  # type: ignore

    def add_task(self, task: Task) -> Any:
        """Add new task to todoist

        Args:
            **kwargs: properties of the task to be added
        """
        self._temp_tasks[task.temp_id] = task  # type: ignore
        return self._command(data=task.dict(exclude_none=True), command_type='item_add')

    def close_task(self, task_id: int | str) -> Any:
        """Complete a task

        Args:
            task_id: the id of the task to complete

        Returns:
            A dict with the result of the task completion command
        """
        if isinstance(task_id, str):
            task_id = int(task_id)
        return self._command(data={'id': task_id}, command_type='item_complete')

    def _command(self, data: Any, command_type: str) -> Any:
        temp_id = data.pop('temp_id', str(uuid.uuid4()))
        command = Command(type=command_type, temp_id=temp_id, args=data)

        self._commands[command.uuid] = command

    def commit(self) -> Any:
        """Commit open commands to Todoist"""
        method_name = inspect.stack()[0][3]
        data = {'commands': [command.dict(exclude_none=True) for command in self._commands.values()]}
        result = self._post(data, method_name)

        for key, value in result['sync_status'].items():
            if value == 'ok':
                self._commands.pop(key)

        for key, value in result['temp_id_mapping'].items():
            task = self._temp_tasks[key]
            task.id = value
            self._temp_tasks.pop(key)

        return result

    def _build_request_data(self, data: Any) -> dict:
        result = {
            'sync_token': self._sync_token,
            **{key: json.dumps(value) for key, value in data.items()}
        }

        return result

    def _post(self, data: dict, method_name: str) -> Any:
        url = f'{BASE_URL}/{APIS[method_name]}'
        dataset = self._build_request_data(data=data)
        response = httpx.post(url=url, data=dataset, headers=self.headers)
        response.raise_for_status()
        result = response.json()

        if 'sync_token' in result:
            self._sync_token = result.pop('sync_token')
        return result


if __name__ == '__main__':
    import os

    apikey_: str = os.environ.get('TODOIST_API')  # type: ignore
    todoist_ = TodoistAPI(api_key=apikey_)
    projects_ = todoist_.sync()
    project_ = todoist_.get_project_by_pattern('Private')
    # project_ = todoist_.get_project(project_id='2198523714')
    task_to_add = Task(content="Buy Milk", project_id="2198523714", due=Due(string="today"))
    todoist_.add_task(task_to_add)
    # added_task_0 = todoist_.add_task(content="Buy Milk", project_id="2198523714", due={'string': "today"})
    # added_task_1 = todoist_.add_task(content="Buy Milk", project_id="2198523714", due={'string': "today"})
    # completed_task_ = todoist_.close_task(task_id=6428239110)
    result_ = todoist_.commit()
    # t = todoist_.get_task(task_id='6429400765')
    print(project_)
