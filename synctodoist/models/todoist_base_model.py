from pydantic import BaseModel, Field

from synctodoist.models.utils import str_uuid4_factory


class TodoistBaseModel(BaseModel):
    """Todoist base model"""
    id: str | int | None
    is_deleted: bool = False
    temp_id: str | None = Field(default_factory=str_uuid4_factory)

    apis: dict[str, str] = {}
    todoist_name: str | None = None
    todoist_field_name: str | None = None
    cache_label: str | None = None

    class Config:
        """Config class for TodoistBaseModel"""
        fields = {
            'apis': {'exclude': True},
            'todoist_name': {'exclude': True},
            'todoist_field_name': {'exclude': True},
            'cache_label': {'exclude': True}
        }

    @property
    def _command_add(self):
        return f'{self.todoist_name}_add'
