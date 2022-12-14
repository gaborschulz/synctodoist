import inspect
import json
import re
import tempfile
import uuid
from pathlib import Path
from typing import Any, Mapping

import httpx
from pydantic import BaseModel

from pytodoist.exceptions import TodoistError
from pytodoist.models import Task, Project, Command

BASE_URL = 'https://api.todoist.com/sync/v9'
APIS = {
    'sync': 'sync',
    'get_task': 'items/get',
    'get_stats': 'completed/get_stats',
    'get_project': 'projects/get',
    'commit': 'sync',
}


class TodoistAPI:  # pylint: disable=too-many-instance-attributes
    """Todoist API class for the new Sync v9 API"""

    def __init__(self, api_key: str, cache_dir: Path | str | None = None):
        self._api_key = api_key
        self._headers = {
            'Authorization': f'Bearer {self._api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.synced = False
        self._sync_token: str = '*'
        self.projects: dict[str, Project] = {}
        self.tasks: dict[str, Task] = {}
        self._commands: dict[str, Command] = {}
        self._temp_tasks: dict[str, Task] = {}

        if not cache_dir:
            cache_dir = tempfile.gettempdir()

        self._cache_dir = cache_dir if isinstance(cache_dir, Path) else Path(cache_dir)

    # PRIVATE METHODS
    def _remove_deleted(self, cached: Mapping[str, BaseModel], received: list[Any], full_sync: bool = False) -> dict[str, BaseModel]:
        received_keys = {x['id'] for x in received}
        result: dict[str, BaseModel] = {}

        if full_sync:
            for key, value in cached.items():
                if key in received_keys:
                    result[key] = value  # type: ignore
        else:
            result = {key: value for key, value in cached.items() if not getattr(value, 'is_deleted', False)}

        return result

    def _write_all_caches(self):
        self._write_cache(self.projects, 'projects')
        self._write_cache(self.tasks, 'tasks')

    def _read_all_caches(self):
        self.projects = self._read_cache('projects')  # type: ignore
        self.tasks = self._read_cache('tasks')  # type: ignore

    def _write_cache(self, data: Mapping[str, BaseModel], cache_name: str):
        cache = {
            'name': cache_name,
            'data': {key: value.dict(exclude_none=True) for key, value in data.items()}
        }

        with (self._cache_dir / f'todoist_{cache_name}.json').open('w', encoding='utf-8') as cache_fp:
            json.dump(cache, cache_fp, default=str)

    def _read_cache(self, cache_name) -> dict[str, BaseModel]:
        cache_mapping = {
            'projects': Project,
            'tasks': Task
        }
        cache_file = self._cache_dir / f'todoist_{cache_name}.json'
        if not cache_file.exists():
            return {}

        with cache_file.open('r', encoding='utf-8') as cache_fp:
            cache = json.load(cache_fp)

        model = cache_mapping.get(cache_name, None)
        if not model:
            return {}

        entities: dict[str, BaseModel] = {key: model(**value) for key, value in cache['data'].items()}
        return entities

    def _write_sync_token(self):
        with (self._cache_dir / 'todoist_sync_token.json').open('w', encoding='utf-8') as cache_fp:
            json.dump({'sync_token': self._sync_token}, cache_fp)

    def _read_sync_token(self) -> str:
        cache_file = self._cache_dir / 'todoist_sync_token.json'
        if not cache_file.exists():
            return '*'

        with cache_file.open('r', encoding='utf-8') as cache_fp:
            return json.load(cache_fp).get('sync_token', '*')  # type: ignore

    def _build_request_data(self, data: Any) -> dict:
        result = {
            'sync_token': self._sync_token,
            **{key: json.dumps(value) for key, value in data.items()}
        }

        return result

    def _post(self, data: dict, method_name: str) -> Any:
        url = f'{BASE_URL}/{APIS[method_name]}'
        dataset = self._build_request_data(data=data)
        response = httpx.post(url=url, data=dataset, headers=self._headers)
        response.raise_for_status()
        result = response.json()

        if 'sync_token' in result:
            self._sync_token = result.pop('sync_token')
        return result

    def _command(self, data: Any, command_type: str) -> None:
        temp_id = data.pop('temp_id', str(uuid.uuid4()))
        command = Command(type=command_type, temp_id=temp_id, args=data)

        self._commands[command.uuid] = command

    # PUBLIC METHODS
    def sync(self, full_sync: bool = False) -> Any:
        """Synchronize with Todoist API

        Returns:
            A dict with all projects
        """
        method_name = inspect.stack()[0][3]
        if not full_sync:
            self._sync_token = self._read_sync_token()

        self._read_all_caches()

        data = {'resource_types': ['projects', 'items']}
        result = self._post(data, method_name)
        # Add new items
        self.projects.update({x['id']: Project(**x) for x in result['projects']})
        self.tasks.update({x['id']: Task(**x) for x in result['items']})

        # Remove deleted items
        self.projects = self._remove_deleted(self.projects, result['projects'], result['full_sync'])  # type: ignore
        self.tasks = self._remove_deleted(self.tasks, result['items'], result['full_sync'])  # type: ignore

        self._write_all_caches()
        self._write_sync_token()

        self.synced = True
        return result

    def get_task(self, task_id: int | str) -> Task:
        """Get task by id

        Args:
            task_id: the id of the task

        Returns:
            A Task instance with all task details
        """
        task = self.tasks.get(str(task_id), None)
        if task:
            return task

        method_name = inspect.stack()[0][3]
        if isinstance(task_id, str) and task_id.isdigit():
            task_id = int(task_id)

        data = {'item_id': task_id}
        result = self._post(data, method_name)
        task = Task(**result.get('item'))
        self.tasks.update({task.id: task})  # type: ignore
        return task

    def get_project(self, project_id: int | str) -> Project:
        """Get project by id

        Args:
            project_id: the id of the project

        Returns:
            A Project instance with all project details
        """
        project = self.projects.get(str(project_id), None)
        if project:
            return project

        method_name = inspect.stack()[0][3]
        if isinstance(project_id, str):
            project_id = int(project_id)

        data = {'project_id': project_id, 'all_data': False}
        result = self._post(data, method_name)
        project = Project(**result['project'])
        self.projects.update({project.id: project})  # type: ignore
        return project

    def get_project_by_pattern(self, pattern: str) -> Project | None:
        """Get a project if its name matches a regex pattern

        Args:
            pattern: the regex pattern against which the project's name is matched

        Returns:
            A Project instance containing the project details

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        if not self.synced:
            raise TodoistError('Run .sync() before you try to find a project based on a pattern')

        compiled_pattern = re.compile(pattern=pattern)
        for project in self.projects.values():
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
        with httpx.Client(headers=self._headers) as client:
            response = client.get(url=url)
            response.raise_for_status()
            return response.json()  # type: ignore

    def add_task(self, task: Task) -> Any:
        """Add new task to todoist

        Args:
            task: a Task instance to add to Todoist
        """
        self._temp_tasks[task.temp_id] = task  # type: ignore
        self._command(data=task.dict(exclude_none=True), command_type='item_add')

    def close_task(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
        """Complete a task

        Args:
            task_id: the id of the task to close
            task: the Task object to close (keyword-only argument)

        Either the task_id or the task must be provided. The task object takes priority over the task_id argument if both are provided
        """
        if not task_id and not task:
            raise TodoistError('Either task_id or task have to be provided')

        if isinstance(task, Task):
            if not task.id:
                task_id = task.temp_id
            else:
                task_id = str(task.id)

        if isinstance(task_id, int):
            task_id = str(task_id)

        self._command(data={'id': task_id}, command_type='item_complete')

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

        self.sync()
        return result


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()
    apikey_: str = os.environ.get('TODOIST_API')  # type: ignore
    todoist_ = TodoistAPI(api_key=apikey_)
    projects_ = todoist_.sync()
    # project_ = todoist_.get_project_by_pattern('Private')
    # project_ = todoist_.get_project(project_id='2198523714')
    # task_to_add = Task(content="Buy Milk", project_id="2198523714", due=Due(string="today"))
    # todoist_.add_task(task_to_add)
    # added_task_0 = todoist_.add_task(content="Buy Milk", project_id="2198523714", due={'string': "today"})
    # added_task_1 = todoist_.add_task(content="Buy Milk", project_id="2198523714", due={'string': "today"})
    # completed_task_ = todoist_.close_task(task_id=6428239110)
    # result_ = todoist_.commit()
    # t = todoist_.get_task(task_id='6429400765')
    # print(project_)
