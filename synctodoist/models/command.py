from pydantic import BaseModel, Field

from synctodoist.models.todoist_base_model import TodoistBaseModel
from synctodoist.models.utils import str_uuid4_factory


class Command(BaseModel):
    """Command model"""
    type: str
    uuid: str = Field(default_factory=str_uuid4_factory)
    temp_id: str | None
    args: dict | list
    is_update_command: bool = Field(False, exclude=True)
    item: TodoistBaseModel | None = Field(None, exclude=True)
