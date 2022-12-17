from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Section


class SectionManager(BaseManager):
    """Section manager"""
    _model = Section
