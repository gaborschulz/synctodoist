from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Label


class LabelManager(BaseManager):
    """Project manager"""
    _model = Label
