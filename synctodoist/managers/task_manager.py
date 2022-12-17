from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Task


class TaskManager(BaseManager):
    """Task manager"""
    _model = Task
