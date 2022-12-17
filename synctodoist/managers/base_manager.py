from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path
from typing import Iterable, Any, Mapping, Type, TYPE_CHECKING

from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.models import Project, TodoistBaseModel

if TYPE_CHECKING:
    from synctodoist.todoist_api import TodoistAPI


class BaseManager:
    """Base manager"""
    _items: Mapping[str, TodoistBaseModel] = {}
    model: Type[TodoistBaseModel]

    def __init__(self, api: TodoistAPI, cache_dir: Path | str | None = None):
        self._api: TodoistAPI = api
        if not cache_dir:
            cache_dir = tempfile.gettempdir()

        self._cache_dir = cache_dir if isinstance(cache_dir, Path) else Path(cache_dir)

    # Pass-through to dict
    def get(self, __key: str, default: Any) -> TodoistBaseModel | None:
        """Get item by key"""
        return self._items.get(__key, default)

    def update(self, _m: dict[str, Project], **kwargs) -> None:
        """Update projects"""
        return self._items.update(_m, **kwargs)  # type: ignore

    def values(self) -> Iterable[TodoistBaseModel]:
        """Get values"""
        return self._items.values()

    def items(self):
        """Get key-value pairs"""
        return self._items.items()

    def __len__(self):
        return len(self._items)

    # Custom methods
    def get_by_id(self, item_id: int | str) -> TodoistBaseModel:
        """Get item by id

        Args:
            item_id: the id of the item

        Returns:
            A TodoistBaseModel instance with all item details
        """
        if item := self.get(str(item_id), None):
            return item  # type: ignore

        if not hasattr(self.model.Config, 'api_get'):
            raise TodoistError(f'{self.model} does not support the get method without syncing. Please, sync your API first.')

    def get_by_pattern(self, pattern: str, field: str = 'name') -> TodoistBaseModel:
        """Get an item if its field matches a regex pattern

        Args:
            pattern: the regex pattern against which the project's name is matched
            field: the field in which the pattern should be searched for (default: name)

        Returns:
            A TodoistBaseModel instance containing the project details

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        if not self._api.synced:
            raise TodoistError('Run .sync() before you try to find a project based on a pattern')

        compiled_pattern = re.compile(pattern=pattern)
        for item in self._items.values():
            if compiled_pattern.findall(getattr(item, field)):
                return item

        raise TodoistError(f'Project matching pattern {pattern} not found')

    def remove_deleted(self, received: list[Any], full_sync: bool = False):
        """Remove deleted items"""
        received_keys = {x['id'] for x in received}
        result: dict[str, TodoistBaseModel] = {}

        if full_sync:
            for key, value in self._items.items():
                if key in received_keys:
                    result[key] = value  # type: ignore
        else:
            result = {key: value for key, value in self._items.items() if not getattr(value, 'is_deleted', False)}

        self._items = result

    def add(self, item: TodoistBaseModel):
        command_manager.add_command(data=item.dict(exclude_none=True), command_type=self.model.Config.command_add, item=item)

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
