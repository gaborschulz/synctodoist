from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Task
from synctodoist.models.project import Project
from synctodoist.models.section import Section


class TaskManager(BaseManager[Task]):
    """Task manager"""
    model = Task

    def get(self, item_id: int | str) -> Task:  # pylint: disable=arguments-renamed
        """Get task by id

        Args:
            item_id: the id of the task

        Returns:
            A Task instance with all task details
        """
        if task := super().get(item_id=item_id):
            return task

        try:
            endpoint = self.model.Config.api_get
            if isinstance(item_id, str) and item_id.isdigit():
                item_id = int(item_id)

            data = {'item_id': item_id}
            result = command_manager.post(data, endpoint)
            task = Task(**result.get('item'))
            self._items.update({task.id: task})  # type: ignore
            return task
        except Exception as ex:
            raise TodoistError(f'Task {item_id} not found') from ex

    def close(self, item: int | str | Task) -> None:
        """Complete a task

        Args:
            item: the Task object or the id of the task to close
        """
        params, task_id = self._extract_params(item)

        command_manager.add_command(data={'id': task_id}, command_type=self.model.Config.command_close, **params)

    def reopen(self, item: int | str | Task) -> None:
        """Reopen a task

        Args:
            item: the Task object or the id of the task to reopen
            item: the Task object to reopen (keyword-only argument)

        Either the task_id or the task must be provided. The task object takes priority over the task_id argument if both are provided
        """

        params, task_id = self._extract_params(item)

        command_manager.add_command(data={'id': task_id}, command_type=self.model.Config.command_reopen, **params)

    def move(self, item: str | int | Task, parent: str | int | Task | None = None, section: str | int | Section | None = None,
             project: str | int | Project | None = None):
        """
        Move task to a different parent, section or project

        One of the parameters has to be provided.

        To move an item from a section to no section, just use the project_id parameter, with the project it currently belongs to as a value.

        Args:
            item: a Task object or the task id that you want to move
            parent: the parent under which you want to place the task
            section: the section in which you want to place the task
            project: the project in which you want to place the task
        """
        if not parent and not section and not project:
            raise TodoistError('At least one out of parent, section or project has to be provided.')

        params, task_id = self._extract_params(item)

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
