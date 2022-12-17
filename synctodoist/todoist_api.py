import inspect
import re
from pathlib import Path
from typing import Any

from synctodoist.exceptions import TodoistError
from synctodoist.managers import ProjectManager, command_manager, TaskManager, LabelManager, SectionManager, ReminderManager
from synctodoist.models import Task, Project, Label, Section, TodoistBaseModel

CACHE_MAPPING = {x.Config.cache_label: x for x in TodoistBaseModel.__subclasses__()}
RESOURCE_TYPES = [x.Config.todoist_resource_type for x in TodoistBaseModel.__subclasses__()]


class TodoistAPI:  # pylint: disable=too-many-instance-attributes
    """Todoist API class for the new Sync v9 API"""

    def __init__(self, api_key: str, cache_dir: Path | str | None = None):
        self.api_key = api_key
        self.synced = False
        self.projects: ProjectManager = ProjectManager(api=self, cache_dir=cache_dir)
        self.tasks: TaskManager = TaskManager(api=self, cache_dir=cache_dir)
        self.labels: LabelManager = LabelManager(api=self, cache_dir=cache_dir)
        self.sections: SectionManager = SectionManager(api=self, cache_dir=cache_dir)
        self.reminders: ReminderManager = ReminderManager(api=self, cache_dir=cache_dir)

        if cache_dir:
            command_manager.cache_dir = cache_dir if isinstance(cache_dir, Path) else Path(cache_dir)

    # PRIVATE METHODS

    def _write_all_caches(self):
        for key in CACHE_MAPPING:
            target = getattr(self, key)
            target.write_cache()

    def _read_all_caches(self):
        for key in CACHE_MAPPING:
            target = getattr(self, key)
            target.read_cache()

    # PUBLIC METHODS
    def sync(self, full_sync: bool = False) -> bool:
        """Synchronize with Todoist API

        Returns:
            True if a full sync was performed, false otherwise
        """
        if not full_sync:
            command_manager.read_sync_token()

        self._read_all_caches()

        data = {'resource_types': RESOURCE_TYPES}
        result = command_manager.post(data, 'sync', self.api_key)

        for key in CACHE_MAPPING:
            target = getattr(self, key)
            model = CACHE_MAPPING[key]
            # Add new items
            target.update({x['id']: model(**x) for x in result[model.Config.todoist_resource_type]})
            # Remove deleted items
            target.remove_deleted(result[model.Config.todoist_resource_type], result['full_sync'])

        self._write_all_caches()
        command_manager.write_sync_token()

        self.synced = True
        return result['full_sync']  # type: ignore

    def get_task(self, task_id: int | str) -> Task:
        """Get task by id

        Args:
            task_id: the id of the task

        Returns:
            A Task instance with all task details
        """
        task = self.tasks.get(str(task_id), None)
        if task:
            return task

        try:
            method_name = inspect.stack()[0][3]
            if isinstance(task_id, str) and task_id.isdigit():
                task_id = int(task_id)

            data = {'item_id': task_id}
            result = command_manager.post(data, method_name, self.api_key)
            task = Task(**result.get('item'))
            self.tasks.update({task.id: task})  # type: ignore
            return task
        except Exception as ex:
            raise TodoistError(f'Task {task_id} not found') from ex

    def get_project(self, project_id: int | str) -> Project:
        """Get project by id

        This is convenience wrapper for TodoistAPI.projects.get_by_id(project_id)
        Args:
            project_id: the id of the project

        Returns:
            A Project instance with all project details
        """
        return self.projects.get_by_id(project_id=project_id)

    def get_project_by_pattern(self, pattern: str) -> Project:
        """Get a project if its name matches a regex pattern

        Args:
            pattern: the regex pattern against which the project's name is matched

        Returns:
            A Project instance containing the project details

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        return self.projects.get_by_pattern(pattern=pattern, field='name')  # type: ignore

    def get_label(self, label_id: int | str) -> Label | None:
        """Get label by id

        Args:
            label_id: the id of the label

        Returns:
            A Label instance with all project details
        """
        label = self.labels.get(str(label_id), None)
        if label:
            return label

        raise TodoistError(f'Label {label_id} not found')

    def get_label_by_pattern(self, pattern: str) -> Label:
        """Get a label if its name matches a regex pattern

        Args:
            pattern: the regex pattern against which the label's name is matched

        Returns:
            A Label instance containing the project details

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        if not self.synced:
            raise TodoistError('Run .sync() before you try to find a label based on a pattern')

        compiled_pattern = re.compile(pattern=pattern)
        for label in self.labels.values():
            if compiled_pattern.findall(label.name):
                return label

        raise TodoistError(f'Label matching {pattern} not found')

    def get_section(self, section_id: int | str) -> Section | None:
        """Get section by id

        Args:
            section_id: the id of the section

        Returns:
            A Section instance with all project details
        """
        section = self.sections.get(str(section_id), None)
        if section:
            return section

        raise TodoistError(f'Section {section_id} not found')

    def get_section_by_pattern(self, pattern: str) -> Section:
        """Get a section if its name matches a regex pattern

        Args:
            pattern: the regex pattern against which the section's name is matched

        Returns:
            A Section instance containing the project details

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        if not self.synced:
            raise TodoistError('Run .sync() before you try to find a section based on a pattern')

        compiled_pattern = re.compile(pattern=pattern)
        for section in self.sections.values():
            if compiled_pattern.findall(section.name):
                return section

        raise TodoistError(f'Section matching {pattern} not found')

    def get_stats(self) -> Any:
        """Get Todoist usage statistics

        Returns:
            A dict with all user stats
        """
        try:
            return command_manager.get('completed/get_stats', self.api_key)
        except Exception as ex:
            raise TodoistError('User stats not available') from ex

    def add(self, item: TodoistBaseModel) -> None:
        """Add new task to todoist

        Args:
            item: a TodoistBaseModel instance to add to Todoist
        """
        command_manager.temp_items[item.temp_id] = item  # type: ignore
        model = type(item)
        command_manager.add_command(data=item.dict(exclude_none=True), command_type=model.Config.command_add)

    def add_task(self, task: Task) -> None:
        """Add new task to todoist.

        This is a convenience method for TodoistAPI.add(item=task).

        Args:
            task: a Task instance to add to Todoist
        """
        self.add(task)

    def close_task(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
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

    def reopen_task(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
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

    def add_project(self, project: Project) -> None:
        """Add new project to todoist.

        This is a convenience method for TodoistAPI.add(item=project).

        Args:
            project: a Project instance to add to Todoist
        """
        self.add(project)

    def add_section(self, section: Section) -> None:
        """Add new section to todoist.

        This is a convenience method for TodoistAPI.add(item=section).

        Args:
            section: a Section instance to add to Todoist
        """
        self.add(section)

    def add_label(self, label: Label) -> None:
        """Add new label to todoist.

        This is a convenience method for TodoistAPI.add(item=label).

        Args:
            label: a Label instance to add to Todoist
        """
        self.add(label)

    def commit(self) -> Any:
        """Commit open commands to Todoist"""
        result = command_manager.commit(self.api_key)

        self.sync()
        return result


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()
    apikey_: str = os.environ.get('TODOIST_API')  # type: ignore
    todoist_ = TodoistAPI(api_key=apikey_)
    todoist_.sync()
    # section = todoist_.get_section(section_id=108544882)
    # print(section)
    # section = todoist_.get_section_by_pattern(pattern="Routines")
    # print(section)
    # project_ = todoist_.get_project_by_pattern('Private')
    # project_ = todoist_.get_project(project_id='2198523714')
    # task_to_add = Task(content="Buy Honey", project_id="2198523714", due=Due(string="today"))
    # todoist_.add(task_to_add)
    # todoist_.commit()
    # todoist_.close_task(task=task_to_add)
    # todoist_.commit()
    # todoist_.reopen_task(task=task_to_add)
    # todoist_.commit()
    # added_task_0 = todoist_.add_task(content="Buy Milk", project_id="2198523714", due={'string': "today"})
    # added_task_1 = todoist_.add_task(content="Buy Milk", project_id="2198523714", due={'string': "today"})
    # completed_task_ = todoist_.close_task(task_id=6428239110)
    # result_ = todoist_.commit()
    # t = todoist_.get_task(task_id='6429400765')
    # print(project_)
    print(todoist_)
