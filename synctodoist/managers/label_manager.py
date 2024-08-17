"""Provides access to Todoist labels"""
import typing
from typing import Any

from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Label

if typing.TYPE_CHECKING:
    from synctodoist.managers.base_manager import TBaseModel


class LabelManager(BaseManager[Label]):
    """
    LabelManager provides access to label objects in Todoist. This class is never instantiated directly, instead, you access it
    through your TodoistAPI class like this.

    Examples:
        >>> api = TodoistAPI()
        >>> label = api.labels.get(item_id=123)
    """
    model = Label

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, model=Label, **kwargs)

    def _remove_deleted(self, received: list[Any], full_sync: bool = False):
        received_keys = {x['id'] for x in received}
        result: dict[str, TBaseModel] = {}

        if full_sync:
            for key, value in self._items.items():
                if key in received_keys:
                    result[key] = value
        else:
            result = {key: value for key, value in self._items.items() if key in received_keys}

        self._items = result
