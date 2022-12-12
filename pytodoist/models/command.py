from pydantic import BaseModel, Field

from pytodoist.models.utils import str_uuid4_factory


class Command(BaseModel):
    """Command model"""
    type: str
    uuid: str = Field(default_factory=str_uuid4_factory)
    temp_id: str | None
    args: dict | list
