from pydantic import BaseModel, Field

from pytodoist.models.utils import str_uuid4_factory


class Project(BaseModel):
    """Project model"""
    id: str | int | None
    name: str
    color: str
    parent_id: str | int | None
    child_order: int | None
    collapsed: bool = False
    shared: bool = False
    sync_id: str | int | None
    is_deleted: bool = False
    is_archived: bool = False
    is_favorite: bool = False
    view_style: str | None
    temp_id: str | None = Field(default_factory=str_uuid4_factory)
