from typing import Any

from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Task
from synctodoist.models.project import Project
from synctodoist.models.section import Section


class TaskManager(BaseManager[Task]):
    """Task manager"""
    model = Task

    def get_by_id(self, task_id: int | str) -> Task:  # pylint: disable=arguments-renamed
        """Get task by id

        Args:
            task_id: the id of the task

        Returns:
            A Task instance with all task details
        """
        if task := super().get_by_id(item_id=task_id):
            return task

        try:
            endpoint = self.model.Config.api_get
            if isinstance(task_id, str) and task_id.isdigit():
                task_id = int(task_id)

            data = {'item_id': task_id}
            result = command_manager.post(data, endpoint, self._api.api_key)
            task = Task(**result.get('item'))
            self._items.update({task.id: task})  # type: ignore
            return task
        except Exception as ex:
            raise TodoistError(f'Task {task_id} not found') from ex

    def close(self, task: int | str | Task) -> None:
        """Complete a task

        Args:
            task: the Task object or the id of the task to close
        """
        params, task_id = self._extract_task_id(task)

        command_manager.add_command(data={'id': task_id}, command_type=self.model.Config.command_close, **params)

    def reopen(self, task: int | str | Task) -> None:
        """Reopen a task

        Args:
            task: the Task object or the id of the task to reopen
            task: the Task object to reopen (keyword-only argument)

        Either the task_id or the task must be provided. The task object takes priority over the task_id argument if both are provided
        """

        params, task_id = self._extract_task_id(task)

        command_manager.add_command(data={'id': task_id}, command_type=self.model.Config.command_reopen, **params)

    def move(self, task: str | int | Task, parent: str | int | Task | None = None, section: str | int | Section | None = None,
             project: str | int | Project | None = None):
        """
        Move task to a different parent, section or project

        One of the parameters has to be provided.

        To move an item from a section to no section, just use the project_id parameter, with the project it currently belongs to as a value.

        Args:
            task: a Task object or the task id that you want to move
            parent: the parent under which you want to place the task
            section: the section in which you want to place the task
            project: the project in which you want to place the task
        """
        if not parent and not section and not project:
            raise TodoistError('At least one out of parent, section or project has to be provided.')

        params, task_id = self._extract_task_id(task)

        data: dict[str, str] = {'id': task_id}
        match parent:
            case Task():
                data['parent_id'] = str(parent.id)
            case int():
                data['parent_id'] = str(parent)
            case str():
                data['parent_id'] = parent

        match section:
            case Section():
                data['section_id'] = str(section.id)
            case int():
                data['section_id'] = str(section)
            case str():
                data['section_id'] = section

        match project:
            case Project():
                data['project_id'] = str(project.id)
            case int():
                data['project_id'] = str(project)
            case str():
                data['project_id'] = project

        command_manager.add_command(data=data, command_type=self.model.Config.command_move, **params)

    @staticmethod
    def _extract_task_id(task: str | int | Task) -> tuple[dict[str, Any], str]:
        params: dict[str, Any] = {}
        task_id: str = ''
        match task:
            case Task():
                params['item'] = task
                params['is_update_command'] = True

                if not task.id:
                    task_id = task.temp_id
                else:
                    task_id = str(task.id)
            case int():
                task_id = str(task_id)
            case str():
                task_id = task
            case _:
                raise TodoistError('task has to be a Task object, a str or an int')
        return params, task_id
