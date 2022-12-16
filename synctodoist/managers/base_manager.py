from typing import Iterable, Any, Mapping

from synctodoist.models import Project, TodoistBaseModel


class BaseManager:
    """Base manager"""
    _items: Mapping[str, TodoistBaseModel] = {}

    def __init__(self, api):
        self._api = api

    def get(self, __key: str, default: Any) -> TodoistBaseModel | None:
        """Get item by key"""
        return self._items.get(__key, default)

    def update(self, _m: dict[str, Project], **kwargs) -> None:
        """Update projects"""
        return self._items.update(_m, **kwargs)  # type: ignore

    def values(self) -> Iterable[TodoistBaseModel]:
        """Get values"""
        return self._items.values()
