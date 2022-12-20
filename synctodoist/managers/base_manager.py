# pylint: disable=line-too-long
from __future__ import annotations

import json
import re
from typing import Iterable, Any, TYPE_CHECKING, TypeVar, Generic, Type

from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.models import TodoistBaseModel, Settings

if TYPE_CHECKING:
    pass

TBaseModel = TypeVar('TBaseModel', bound=TodoistBaseModel)  # pylint: disable=invalid-name


class BaseManager(Generic[TBaseModel]):
    """Base manager"""
    _items: dict[str, TBaseModel]
    model: Type[TBaseModel]

    def __init__(self, settings: Settings):
        self._items = {}
        self.settings = settings

    # region Pass-through to dict
    def _dict_get(self, __key: str, default: Any) -> TBaseModel | None:
        return self._items.get(__key, default)

    def _dict_update(self, _m: dict[str, TBaseModel], **kwargs) -> None:
        return self._items.update(_m, **kwargs)

    def _dict_values(self) -> Iterable[TBaseModel]:
        return self._items.values()

    def _dict_items(self):
        return self._items.items()

    def __len__(self):
        return len(self._items)

    # endregion

    # region Private methods
    def _extract_params(self, item: str | int | TBaseModel) -> tuple[dict[str, Any], str]:
        params: dict[str, Any] = {}
        match item:
            case self.model():
                params['item'] = item
                params['is_update_command'] = True

                if not item.id:
                    item_id = item.temp_id
                else:
                    item_id = str(item.id)
            case int():
                item_id = str(item)
            case str():
                item_id = item
            case _:
                raise TodoistError('task has to be a Task object, a str or an int')
        return params, item_id

    def _remove_deleted(self, received: list[Any], full_sync: bool = False):
        received_keys = {x['id'] for x in received}
        result: dict[str, TBaseModel] = {}

        if full_sync:
            for key, value in self._items.items():
                if key in received_keys:
                    result[key] = value
        else:
            result = {key: value for key, value in self._items.items() if not getattr(value, 'is_deleted', False)}

        self._items = result

    def _read_cache(self):
        cache_file = self.settings.cache_dir / f'todoist_{self.model.Config.cache_label}.json'
        if not cache_file.exists():
            return

        with cache_file.open('r', encoding='utf-8') as cache_fp:
            cache = json.load(cache_fp)

        self._items = {key: self.model(**value) for key, value in cache['data'].items()}

    def _write_cache(self):
        cache_file = self.settings.cache_dir / f'todoist_{self.model.Config.cache_label}.json'
        cache = {
            'name': self.model.Config.cache_label,
            'data': {key: value.dict(exclude_none=True) for key, value in self._items.items()}
        }

        with cache_file.open('w', encoding='utf-8') as cache_fp:
            json.dump(cache, cache_fp, default=str)

    # endregion

    # region Manager methods
    def get(self, item_id: int | str) -> TBaseModel | None:
        """Get item by id

        Args:
            item_id: the id of the item

        Returns:
            A TodoistBaseModel instance with all item details
        """
        if item := self._dict_get(str(item_id), None):
            return item

        if not hasattr(self.model.Config, 'api_get'):
            raise TodoistError(f'{self.model} does not support the get method without syncing. Please, sync your API first.')

        return None

    def find(self, pattern: str, field: str = 'name', return_all: bool = False) -> TBaseModel | list[TBaseModel]:
        """Get an item if its field matches a regex pattern

        Args:
            pattern: the regex pattern against which the project's name is matched
            field: the field in which the pattern should be searched for (default: name)
            return_all: returns only the first matching item if set to False (default), otherwise returns all matching items as a list

        Returns:
            A TodoistBaseModel instance containing the project details or a list of TodoistBaseModel instances. Raises a TodoistError if return_all is set to False and no matching item is found.

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        items: list[TBaseModel] = []
        compiled_pattern = re.compile(pattern=pattern)
        for item in self._items.values():
            if compiled_pattern.findall(getattr(item, field)):
                if not return_all:
                    return item

                items.append(item)

        if not return_all:
            raise TodoistError(f'Project matching pattern {pattern} not found. Run .sync() before you try to find a project based on a pattern.')

        return items

    def add(self, item: TBaseModel):
        """Add new item to command_manager queue"""
        command_manager.add_command(data=item.dict(exclude_none=True, exclude_defaults=True), command_type=self.model.Config.command_add, item=item)

    def delete(self, item: int | str | TBaseModel) -> None:
        """Delete an item

        Args:
            item: the id of the item to delete as a string or an int, or a TodoistBaseModel instance

        Either the item_id or the item must be provided. The item object takes priority over the item_id argument if both are provided
        """

        _, item_id = self._extract_params(item)

        command_manager.add_command(data={'id': item_id}, command_type=self.model.Config.command_delete)

    def update(self, item: int | str | TBaseModel, updated_item: TBaseModel):
        """
        Update the item identified by item_id with the data from item

        Args:
            item: the item_id of the item to update
            updated_item: the data to use for the update
        """
        params, item_id = self._extract_params(item)

        command_manager.add_command(data={'id': item_id, **updated_item.dict(exclude={'id'}, exclude_none=True, exclude_defaults=True)},
                                    command_type=self.model.Config.command_update, **params)  # type: ignore

    # endregion
