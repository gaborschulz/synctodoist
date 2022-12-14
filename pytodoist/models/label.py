from pydantic import BaseModel, Field

from pytodoist.models.utils import str_uuid4_factory


class Label(BaseModel):
    """Label model"""
    id: str | int | None
    name: str
    color: str
    item_order: int
    is_deleted: bool = False
    is_favorite: bool = False
    temp_id: str | None = Field(default_factory=str_uuid4_factory)
