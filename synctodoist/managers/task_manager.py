from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Task


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

    def close(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
        """Complete a task

        Args:
            task_id: the id of the task to close
            task: the Task object to close (keyword-only argument)

        Either the task_id or the task must be provided. The task object takes priority over the task_id argument if both are provided
        """
        if not task_id and not task:
            raise TodoistError('Either task_id or task have to be provided')

        if isinstance(task, Task):
            if not task.id:
                task_id = task.temp_id
            else:
                task_id = str(task.id)

        if isinstance(task_id, int):
            task_id = str(task_id)

        command_manager.add_command(data={'id': task_id}, command_type='item_complete')

    def reopen(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
        """Uncomplete a task

        Args:
            task_id: the id of the task to reopen
            task: the Task object to reopen (keyword-only argument)

        Either the task_id or the task must be provided. The task object takes priority over the task_id argument if both are provided
        """
        if not task_id and not task:
            raise TodoistError('Either task_id or task have to be provided')

        if isinstance(task, Task):
            if not task.id:
                task_id = task.temp_id
            else:
                task_id = str(task.id)

        if isinstance(task_id, int):
            task_id = str(task_id)

        command_manager.add_command(data={'id': task_id}, command_type='item_uncomplete')
