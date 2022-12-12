from pydantic import BaseModel


class Project(BaseModel):
    """Project model"""
    id: str | int | None
    name: str
    color: str
    parent_id: str | int | None
    child_order: int | None
    collapsed: bool
    shared: bool
    sync_id: str | int | None
    is_deleted: bool
    is_archived: bool
    is_favorite: bool
    view_style: str | None
