from pydantic import BaseModel, Field

from pytodoist.models.utils import str_uuid4_factory


class Label(BaseModel):
    """Label model"""
    id: str | int | None
    name: str
    color: str | None
    item_order: int | None
    is_deleted: bool = False
    is_favorite: bool = False
    temp_id: str | None = Field(default_factory=str_uuid4_factory)
