import inspect
import json
from typing import Any

import httpx

BASE_URL = 'https://api.todoist.com/sync/v9'
APIS = {
    'sync': 'sync',
    'get_task': 'items/get',
    'get_stats': 'completed/get_stats'
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

    def sync(self) -> Any:
        """Synchronize with Todoist API"""
        method_name = inspect.stack()[0][3]
        data = {'resource_types': ['projects']}
        result = self._post(data, method_name)
        return result

    def get_task(self, task_id: int) -> Any:
        """Get task from Todoist API by id"""
        method_name = inspect.stack()[0][3]
        data = {'item_id': task_id}
        result = self._post(data, method_name)
        return result

    def get_stats(self) -> dict:
        """Get Todoist usage statistics"""
        method_name = inspect.stack()[0][3]
        url = f'{BASE_URL}/{APIS[method_name]}'
        with httpx.Client(headers=self.headers) as client:
            response = client.get(url=url)
            response.raise_for_status()
            return response.json()  # type: ignore

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
    # projects = todoist.sync()
    task = todoist.get_task(task_id=2865433246)
    print(task)
