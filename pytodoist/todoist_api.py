import inspect
import json
import re
import uuid
from typing import Any

import httpx

BASE_URL = 'https://api.todoist.com/sync/v9'
APIS = {
    'sync': 'sync',
    'get_task': 'items/get',
    'get_stats': 'completed/get_stats',
    'get_project': 'projects/get',
    '_command': 'sync',
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
        self.projects = []

    def sync(self) -> Any:
        """Synchronize with Todoist API

        Returns:
            A dict with all projects
        """
        method_name = inspect.stack()[0][3]
        data = {'resource_types': ['projects']}
        result = self._post(data, method_name)
        self.projects = result['projects']
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
        return result

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
        return result

    def get_project_by_pattern(self, pattern: str) -> Any:
        """Get a project if its name matches a regex pattern

        Args:
            pattern: the regex pattern against which the project's name is matched

        Returns:
            A dict containing the project details
        """
        compiled_pattern = re.compile(pattern=pattern)
        for project in self.projects:
            if compiled_pattern.findall(project['name']):
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

    def add_task(self, **kwargs) -> Any:
        """Add new task to todoist

        Args:
            **kwargs: properties of the task to be added
        """
        return self._command(data=kwargs, command_type='item_add')

    def complete_task(self, task_id: int | str) -> Any:
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
        method_name = inspect.stack()[0][3]
        data = {'commands': [
            {
                "type": command_type,
                "temp_id": str(uuid.uuid4()),
                "uuid": str(uuid.uuid4()),
                "args": data
            }
        ]}
        result = self._post(data, method_name)
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

    apikey: str = os.environ.get('TODOIST_API')  # type: ignore
    todoist = TodoistAPI(api_key=apikey)
    projects = todoist.sync()
    project_ = todoist.get_project_by_pattern('Private')
    project_ = todoist.get_project(project_id='2198523714')
    # added_task = todoist.add_task(content="Buy Milk", project_id="2198523714", due={'string': "today"})
    completed_task = todoist.complete_task(task_id=6428239110)
    print(completed_task)
