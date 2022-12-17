import json
import tempfile
import uuid
from pathlib import Path
from typing import Any

import httpx

from synctodoist.models import Command, TodoistBaseModel

BASE_URL = 'https://api.todoist.com/sync/v9'
APIS = {
    'get_task': 'items/get',
    'get_project': 'projects/get',
}

_headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

commands: dict[str, Command] = {}
temp_items: dict[str, TodoistBaseModel] = {}
SYNC_TOKEN: str = '*'
cache_dir = Path(tempfile.gettempdir())


def add_command(data: Any, command_type: str, item: TodoistBaseModel | None = None) -> None:
    """Add a Todoist command to command cache

    Args:
        data: The dataset to submit with the command
        command_type: The type of the command
        item: the TodoistBaseModel sublcass item to which this command is linked
    """
    if item and getattr(item, 'temp_id', None):
        temp_items[str(item.temp_id)] = item

    temp_id = data.pop('temp_id', str(uuid.uuid4()))
    command = Command(type=command_type, temp_id=temp_id, args=data)

    commands[command.uuid] = command


def _build_request_data(data: Any) -> dict:
    result = {
        'sync_token': SYNC_TOKEN,
        **{key: json.dumps(value) for key, value in data.items()}
    }

    return result


def post(data: dict, endpoint: str, api_key: str) -> Any:
    """Post data to Todoist"""
    global SYNC_TOKEN  # pylint: disable=global-statement

    url = f'{BASE_URL}/{endpoint}'
    _headers.update({'Authorization': f'Bearer {api_key}'})

    dataset = _build_request_data(data=data)
    response = httpx.post(url=url, data=dataset, headers=_headers)
    response.raise_for_status()
    result = response.json()

    if 'sync_token' in result:
        SYNC_TOKEN = result.pop('sync_token')
    return result


def get(endpoint: str, api_key: str) -> Any:
    """Get data from Todoist"""
    url = f'{BASE_URL}/{endpoint}'
    _headers.update({'Authorization': f'Bearer {api_key}'})
    with httpx.Client(headers=_headers) as client:
        response = client.get(url=url)
        response.raise_for_status()
        return response.json()  # type: ignore


def commit(api_key: str) -> Any:
    """Commit open commands to Todoist"""
    endpoint = 'sync'
    data = {'commands': [command.dict(exclude_none=True) for command in commands.values()]}
    result = post(data, endpoint, api_key)

    for key, value in result['sync_status'].items():
        if value == 'ok':
            commands.pop(key)

    for key, value in result['temp_id_mapping'].items():
        item = temp_items[key]
        item.id = value  # type: ignore
        temp_items.pop(key)  # type: ignore

    return result


def write_sync_token():
    """Store the sync token"""
    with (cache_dir / 'todoist_sync_token.json').open('w', encoding='utf-8') as cache_fp:
        json.dump({'sync_token': SYNC_TOKEN}, cache_fp)


def read_sync_token():
    """Load the sync token"""
    global SYNC_TOKEN  # pylint: disable=global-statement
    cache_file = cache_dir / 'todoist_sync_token.json'
    if not cache_file.exists():
        SYNC_TOKEN = '*'  # nosec

    with cache_file.open('r', encoding='utf-8') as cache_fp:
        SYNC_TOKEN = json.load(cache_fp).get('sync_token', '*')  # type: ignore
