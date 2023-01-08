from __future__ import annotations

import typing

from .enums import ColorEnum
from .todoist_base_model import TodoistBaseModel

if typing.TYPE_CHECKING:
    from .task import Task


class Project(TodoistBaseModel):
    """
    Project model

    Attributes:
        name: The name of the project
        color: The color of the project
        parent_id: The id of the parent project
        child_order: The order of the project. Defines the position of the project among all the projects with the same parent_id
        collapsed: Whether the project's subprojects are collapsed
        shared: Whether the project is shared
        sync_id: Identifier to find the match between different copies of shared projects. When you share a project, its copy has a different ID for your
                 collaborators. To find a project in a different account that matches yours, you can use the `sync_id` attribute. For non-shared projects
                 the attribute is set to `None`
        is_archived: Whether the project is marked as archived
        is_favorite: Whether the project is a favorite
        inbox_project: Whether the project is Inbox
        team_inbox: Whether the project is TeamInbox
        view_style: A string value (either `list` or `board`). This determines the way the project is displayed within the Todoist clients.

    Note:
        This class inherits all the properties of [`TodoistBaseModel`](models.md#todoistbasemodel)
    """
    name: str
    color: ColorEnum | None
    parent_id: str | int | None
    child_order: int | None
    collapsed: bool = False
    shared: bool = False
    sync_id: str | int | None
    is_archived: bool = False
    is_favorite: bool = False
    view_style: str | None
    inbox_project: bool = False
    team_inbox: bool = False

    class Config:
        """Config for Project model"""
        cache_label: str = 'projects'
        todoist_name: str = 'project'
        todoist_resource_type: str = 'projects'
        command_add: str = 'project_add'
        command_delete: str = 'project_delete'
        command_update: str = 'project_update'
        api_get: str = 'projects/get'

    @property
    def tasks(self) -> list[Task]:  # pylint: disable=used-before-assignment
        """
        The list of tasks related to this project

        Returns:
            A list of `Task` instances
        """
        from synctodoist.managers import TaskManager  # pylint: disable=import-outside-toplevel
        task_manager = TaskManager()
        return task_manager.find(pattern=self.id, field='project_id', return_all=True)  # type: ignore
