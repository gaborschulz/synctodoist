from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Project


class ProjectManager(BaseManager):
    """Project manager model"""
    _model = Project

    def __init__(self, api):
        super().__init__(api=api, model=self._model)
