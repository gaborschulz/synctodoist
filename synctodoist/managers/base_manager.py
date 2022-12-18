from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path
from typing import Iterable, Any, TYPE_CHECKING, TypeVar, Generic, Type

from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.models import TodoistBaseModel

if TYPE_CHECKING:
    from synctodoist.todoist_api import TodoistAPI

DataT = TypeVar('DataT', bound=TodoistBaseModel)


class BaseManager(Generic[DataT]):
    """Base manager"""
    _items: dict[str, DataT] = {}
    model: Type[DataT]

    def __init__(self, api: TodoistAPI, cache_dir: Path | str | None = None):
        self._api: TodoistAPI = api
        if not cache_dir:
            cache_dir = tempfile.gettempdir()

        self._cache_dir = cache_dir if isinstance(cache_dir, Path) else Path(cache_dir)

    # Pass-through to dict
    def get(self, __key: str, default: Any) -> DataT | None:
        """Get item by key"""
        return self._items.get(__key, default)

    def update_dict(self, _m: dict[str, DataT], **kwargs) -> None:
        """Update projects"""
        return self._items.update(_m, **kwargs)

    def values(self) -> Iterable[DataT]:
        """Get values"""
        return self._items.values()

    def items(self):
        """Get key-value pairs"""
        return self._items.items()

    def __len__(self):
        return len(self._items)

    # Custom methods
    def get_by_id(self, item_id: int | str) -> DataT | None:
        """Get item by id

        Args:
            item_id: the id of the item

        Returns:
            A TodoistBaseModel instance with all item details
        """
        if item := self.get(str(item_id), None):
            return item

        if not hasattr(self.model.Config, 'api_get'):
            raise TodoistError(f'{self.model} does not support the get method without syncing. Please, sync your API first.')

        return None

    def get_by_pattern(self, pattern: str, field: str = 'name', return_all: bool = False) -> DataT | list[DataT]:
        """Get an item if its field matches a regex pattern

        Args:
            pattern: the regex pattern against which the project's name is matched
            field: the field in which the pattern should be searched for (default: name)
            return_all: returns only the first matching item if set to False (default), otherwise returns all matching items as a list

        Returns:
            A TodoistBaseModel instance containing the project details or a list of TodoistBaseModel instances. Raises a TodoistError if return_all is set
            to False and no matching item is found.

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        if not self._api.synced:
            raise TodoistError('Run .sync() before you try to find a project based on a pattern')

        items: list[DataT] = []
        compiled_pattern = re.compile(pattern=pattern)
        for item in self._items.values():
            if compiled_pattern.findall(getattr(item, field)):
                if not return_all:
                    return item

                items.append(item)

        if not return_all:
            raise TodoistError(f'Project matching pattern {pattern} not found')

        return items

    def remove_deleted(self, received: list[Any], full_sync: bool = False):
        """Remove deleted items"""
        received_keys = {x['id'] for x in received}
        result: dict[str, DataT] = {}

        if full_sync:
            for key, value in self._items.items():
                if key in received_keys:
                    result[key] = value
        else:
            result = {key: value for key, value in self._items.items() if not getattr(value, 'is_deleted', False)}

        self._items = result

    def add(self, item: DataT):
        """Add new item to command_manager queue"""
        command_manager.add_command(data=item.dict(exclude_none=True, exclude_defaults=True), command_type=self.model.Config.command_add, item=item)

    def read_cache(self):
        """Read cached data"""
        cache_file = self._cache_dir / f'todoist_{self.model.Config.cache_label}.json'
        if not cache_file.exists():
            return

        with cache_file.open('r', encoding='utf-8') as cache_fp:
            cache = json.load(cache_fp)

        self._items = {key: self.model(**value) for key, value in cache['data'].items()}

    def write_cache(self):
        """Write data to cache"""
        cache_file = self._cache_dir / f'todoist_{self.model.Config.cache_label}.json'
        cache = {
            'name': self.model.Config.cache_label,
            'data': {key: value.dict(exclude_none=True) for key, value in self._items.items()}
        }

        with cache_file.open('w', encoding='utf-8') as cache_fp:
            json.dump(cache, cache_fp, default=str)

    def delete(self, item_id: int | str | None = None, *, item: DataT | None = None) -> None:
        """Delete an item

        Args:
            item_id: the id of the item to delete
            item: the Label object to delete (keyword-only argument)

        Either the item_id or the item must be provided. The item object takes priority over the item_id argument if both are provided
        """

        if not item_id and not item:
            raise TodoistError('Either label_id or label have to be provided')

        if isinstance(item, self.model):
            if not item.id:
                item_id = item.temp_id
            else:
                item_id = str(item.id)

        if isinstance(item_id, int):
            item_id = str(item_id)

        command_manager.add_command(data={'id': item_id}, command_type=self.model.Config.command_delete)

    def update(self, item_id: int | str | DataT, item: DataT):
        """
        Update the item identified by item_id with the data from item

        Args:
            item_id: the item_id of the item to update
            item: the data to use for the update
        """
        data_item_id: str = item_id  # type: ignore
        if isinstance(item_id, self.model):
            if not item_id.id:
                data_item_id = item_id.temp_id  # type: ignore
            else:
                data_item_id = str(item_id.id)

        if isinstance(item_id, int):
            data_item_id = str(item_id)

        command_manager.add_command(data={'id': data_item_id, **item.dict(exclude={'id'}, exclude_none=True, exclude_defaults=True)},
                                    command_type='label_update', item=item_id, is_update_command=True)  # type: ignore
