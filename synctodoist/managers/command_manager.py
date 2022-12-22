# pylint: disable=invalid-name
import json
import uuid
from typing import Any

import httpx

from synctodoist.exceptions import TodoistError
from synctodoist.models import Command, TodoistBaseModel, Settings

BASE_URL = 'https://api.todoist.com/sync/v9'

_headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

commands: dict[str, Command] = {}
temp_items: dict[str, TodoistBaseModel] = {}
SYNC_TOKEN: str = '*'
settings: Settings = Settings()
full_sync_count = 0
partial_sync_count = 0


def add_command(data: Any, command_type: str, item: TodoistBaseModel | None = None, is_update_command: bool = False) -> None:
    """Add a Todoist command to command cache

    Args:
        data: The dataset to submit with the command
        command_type: The type of the command
        item: the TodoistBaseModel sublcass item to which this command is linked
        is_update_command: True if this command should update item on successful execution
    """
    if item and getattr(item, 'temp_id', None):
        temp_items[str(item.temp_id)] = item

    temp_id = data.pop('temp_id', str(uuid.uuid4()))
    extra_params: dict[str, Any] = {}
    if item:
        extra_params['item'] = item
        extra_params['is_update_command'] = is_update_command
    command = Command(type=command_type, temp_id=temp_id, args=data, **extra_params)

    commands[command.uuid] = command


def _build_request_data(data: Any) -> dict:
    result = {
        'sync_token': SYNC_TOKEN,
        **{key: json.dumps(value) for key, value in data.items()}
    }

    return result


def post(data: dict, endpoint: str) -> Any:
    """Post data to Todoist"""
    global SYNC_TOKEN  # pylint: disable=global-statement

    url = f'{BASE_URL}/{endpoint}'
    _headers.update({'Authorization': f'Bearer {settings.api_key}'})

    dataset = _build_request_data(data=data)
    response = httpx.post(url=url, data=dataset, headers=_headers)
    response.raise_for_status()
    result = response.json()

    if 'sync_token' in result:
        SYNC_TOKEN = result.pop('sync_token')
    return result


def get(endpoint: str) -> Any:
    """Get data from Todoist"""
    url = f'{BASE_URL}/{endpoint}'
    _headers.update({'Authorization': f'Bearer {settings.api_key}'})
    with httpx.Client(headers=_headers) as client:
        response = client.get(url=url)
        response.raise_for_status()
        return response.json()  # type: ignore


def _update_item(command):
    values = command.args.copy()
    values.pop('id')
    command.item.refresh(**values)


def commit() -> Any:
    """Commit open commands to Todoist"""
    global full_sync_count  # pylint: disable=global-statement
    global partial_sync_count  # pylint: disable=global-statement

    endpoint = 'sync'
    data = {'commands': [command.dict(exclude_none=True, exclude_defaults=True) for command in commands.values()]}
    result = post(data, endpoint)

    if result.get('full_sync', False):
        full_sync_count += 1
    else:
        partial_sync_count += 1

    errors = []
    for key, value in result['sync_status'].items():
        command = commands.pop(key)
        if 'error' in value:
            errors.append({key: value})
        if value == 'ok':
            if command.item and command.is_update_command:
                _update_item(command)

    if errors:
        raise TodoistError(f'Sync Error: {errors}')

    for key, value in result['temp_id_mapping'].items():
        item = temp_items[key]
        item.id = value  # type: ignore
        temp_items.pop(key)  # type: ignore

    return result


def write_sync_token():
    """Store the sync token"""
    if not settings.cache_dir.exists():
        settings.cache_dir.mkdir(parents=True, exist_ok=True)

    with (settings.cache_dir / 'todoist_sync_token.json').open('w', encoding='utf-8') as cache_fp:
        json.dump({'sync_token': SYNC_TOKEN}, cache_fp)


def read_sync_token():
    """Load the sync token"""
    global SYNC_TOKEN  # pylint: disable=global-statement
    cache_file = settings.cache_dir / 'todoist_sync_token.json'
    if not cache_file.exists():
        SYNC_TOKEN = '*'  # nosec
        return

    with cache_file.open('r', encoding='utf-8') as cache_fp:
        SYNC_TOKEN = json.load(cache_fp).get('sync_token', '*')  # type: ignore
