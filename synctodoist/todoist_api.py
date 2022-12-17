from pathlib import Path
from typing import Any

from synctodoist.exceptions import TodoistError
from synctodoist.managers import ProjectManager, command_manager, TaskManager, LabelManager, SectionManager, ReminderManager
from synctodoist.models import Task, Project, Label, Section, TodoistBaseModel, Reminder

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

    # region PRIVATE METHODS

    def _write_all_caches(self):
        for key in CACHE_MAPPING:
            target = getattr(self, key)
            target.write_cache()

    def _read_all_caches(self):
        for key in CACHE_MAPPING:
            target = getattr(self, key)
            target.read_cache()

    # endregion

    # region PUBLIC METHODS
    # region Global methods
    def add(self, item: TodoistBaseModel) -> None:
        """Add new task to todoist

        Args:
            item: a TodoistBaseModel instance to add to Todoist
        """
        # type: ignore
        model = type(item)
        key = model.Config.cache_label
        model_manager = getattr(self, key)
        model_manager.add(item=item)

    def commit(self) -> Any:
        """Commit open commands to Todoist"""
        result = command_manager.commit(self.api_key)

        self.sync()
        return result

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

    # endregion

    # region Label methods
    def add_label(self, label: Label) -> None:
        """Add new label to todoist.

        This is a convenience method for TodoistAPI.add(item=label).

        Args:
            label: a Label instance to add to Todoist
        """
        self.add(label)

    def delete_label(self, label_id: int | str | None = None, *, label: Label | None = None) -> None:
        """Delete a label

        Args:
            label_id: the id of the label to delete
            label: the Label object to delete (keyword-only argument)

        Either the label_id or the label must be provided. The label object takes priority over the label_id argument if both are provided
        """
        self.labels.delete(label_id=label_id, label=label)

    def get_label(self, label_id: int | str) -> Label | None:
        """Get label by id

        Args:
            label_id: the id of the label

        Returns:
            A Label instance with all project details
        """
        return self.labels.get_by_id(item_id=label_id)  # type: ignore

    def get_label_by_pattern(self, pattern: str, return_all: bool = False) -> Label | list[Label]:
        """Get a label if its name matches a regex pattern

        Args:
            pattern: the regex pattern against which the label's name is matched
            return_all: returns only the first matching item if set to False (default), otherwise returns all matching items as a list

        Returns:
            A Label instance containing the project details

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        return self.labels.get_by_pattern(pattern=pattern, field='name', return_all=return_all)

    # endregion

    # region Project methods
    def add_project(self, project: Project) -> None:
        """Add new project to todoist.

        This is a convenience method for TodoistAPI.add(item=project).

        Args:
            project: a Project instance to add to Todoist
        """
        self.add(project)

    def delete_project(self, project_id: int | str | None = None, *, project: Project | None = None) -> None:
        """Delete a project

        Args:
            project_id: the id of the project to delete
            project: the Project object to delete (keyword-only argument)

        Either the project_id or the project must be provided. The project object takes priority over the project_id argument if both are provided
        """
        self.projects.delete(project_id=project_id, project=project)

    def get_project(self, project_id: int | str) -> Project:
        """Get project by id

        This is convenience wrapper for TodoistAPI.projects.get_by_id(project_id)
        Args:
            project_id: the id of the project

        Returns:
            A Project instance with all project details
        """
        return self.projects.get_by_id(project_id=project_id)

    def get_project_by_pattern(self, pattern: str, return_all: bool = False) -> Project | list[Project]:
        """Get a project if its name matches a regex pattern

        Args:
            pattern: the regex pattern against which the project's name is matched
            return_all: returns only the first matching item if set to False (default), otherwise returns all matching items as a list

        Returns:
            A Project instance containing the project details

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        return self.projects.get_by_pattern(pattern=pattern, field='name', return_all=return_all)

    # endregion

    # region Reminder methods
    def add_reminder(self, reminder: Reminder) -> None:
        """Add new reminder to todoist.

        This is a convenience method for TodoistAPI.add(item=reminder).

        Args:
            reminder: a Reminder instance to add to Todoist
        """
        self.add(reminder)

    def delete_reminder(self, reminder_id: int | str | None = None, *, reminder: Reminder | None = None) -> None:
        """Delete a reminder

        Args:
            reminder_id: the id of the reminder to delete
            reminder: the Reminder object to delete (keyword-only argument)

        Either the reminder_id or the reminder must be provided. The reminder object takes priority over the reminder_id argument if both are provided
        """
        self.reminders.delete(reminder_id=reminder_id, reminder=reminder)

    def get_reminder(self, reminder_id: int | str) -> Reminder | None:
        """Get reminder by id

        Args:
            reminder_id: the id of the reminder

        Returns:
            A Reminder instance with all project details
        """
        return self.reminders.get_by_id(item_id=reminder_id)  # type: ignore

    # endregion

    # region Section methods
    def add_section(self, section: Section) -> None:
        """Add new section to todoist.

        This is a convenience method for TodoistAPI.add(item=section).

        Args:
            section: a Section instance to add to Todoist
        """
        self.add(section)

    def delete_section(self, section_id: int | str | None = None, *, section: Section | None = None) -> None:
        """Delete a section

        Args:
            section_id: the id of the section to delete
            section: the Section object to delete (keyword-only argument)

        Either the section_id or the section must be provided. The section object takes priority over the section_id argument if both are provided
        """
        self.sections.delete(section_id=section_id, section=section)

    def get_section(self, section_id: int | str) -> Section | None:
        """Get section by id

        Args:
            section_id: the id of the section

        Returns:
            A Section instance with all project details
        """
        return self.sections.get_by_id(item_id=section_id)

    def get_section_by_pattern(self, pattern: str, return_all: bool = False) -> Section | list[Section]:
        """Get a section if its name matches a regex pattern

        Args:
            pattern: the regex pattern against which the section's name is matched
            return_all: returns only the first matching item if set to False (default), otherwise returns all matching items as a list

        Returns:
            A Section instance containing the project details

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        return self.sections.get_by_pattern(pattern=pattern, field='name', return_all=return_all)

    # endregion

    # region Task methods
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
        self.tasks.close(task_id=task_id, task=task)

    def delete_task(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
        """Delete a task

        Args:
            task_id: the id of the task to delete
            task: the Task object to delete (keyword-only argument)

        Either the task_id or the task must be provided. The task object takes priority over the task_id argument if both are provided
        """
        self.tasks.delete(task_id=task_id, task=task)

    def get_task(self, task_id: int | str) -> Task:
        """Get task by id

        Args:
            task_id: the id of the task

        Returns:
            A Task instance with all task details
        """
        return self.tasks.get_by_id(task_id=task_id)

    def get_task_by_pattern(self, pattern: str, return_all: bool = False) -> Task | list[Task]:
        """Get a project if its name matches a regex pattern

        Args:
            pattern: the regex pattern against which the project's name is matched
            return_all: returns only the first matching item if set to False (default), otherwise returns all matching items as a list

        Returns:
            A Project instance containing the project details

        IMPORTANT: You have to run the .sync() method first for this to work
        """
        return self.tasks.get_by_pattern(pattern=pattern, field='content', return_all=return_all)

    def reopen_task(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
        """Uncomplete a task

        Args:
            task_id: the id of the task to reopen
            task: the Task object to reopen (keyword-only argument)

        Either the task_id or the task must be provided. The task object takes priority over the task_id argument if both are provided
        """
        self.tasks.reopen(task_id=task_id, task=task)

    # endregion

    # region User methods
    def get_stats(self) -> Any:
        """Get Todoist usage statistics

        Returns:
            A dict with all user stats
        """
        try:
            return command_manager.get('completed/get_stats', self.api_key)
        except Exception as ex:
            raise TodoistError('User stats not available') from ex
    # endregion
    # endregion


if __name__ == '__main__':  # pragma: no cover
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
