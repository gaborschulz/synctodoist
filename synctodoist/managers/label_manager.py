"""Provides access to Todoist labels"""
from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Label


class LabelManager(BaseManager[Label]):
    """
    LabelManager provides access to label objects in Todoist. This class is never instantiated directly, instead, you access it
    through your TodoistAPI class like this.

    Examples:
        >>> api = TodoistAPI()
        >>> label = api.labels.get(item_id=123)
    """
    model = Label
