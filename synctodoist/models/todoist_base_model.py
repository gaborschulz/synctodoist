from pydantic import BaseModel, Field, validate_model

from synctodoist.models.utils import str_uuid4_factory


class TodoistBaseModel(BaseModel):
    """Todoist base model"""
    id: str | int | None
    is_deleted: bool = False
    temp_id: str = Field(default_factory=str_uuid4_factory)

    class Config:
        """Config for TodoistBaseModel"""
        apis: dict[str, str] = {}
        todoist_name: str = ''
        todoist_resource_type: str = ''
        cache_label: str = ''
        command_add: str = ''
        command_delete: str = ''
        command_update: str = ''
        api_get: str = ''

    def refresh(self, **data):
        """
        Update model instance with the content of data
        Args:
            **data: keyword arguments with the field to update
        """
        values, fields, error = validate_model(self.__class__, data)

        if error:
            raise error

        for field in fields:
            setattr(self, field, values[field])
