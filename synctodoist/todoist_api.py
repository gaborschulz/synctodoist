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
            target.update_dict({x['id']: model(**x) for x in result[model.Config.todoist_resource_type]})
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
        if label:
            self.labels.delete(item=label)
        elif label_id:
            self.labels.delete(item=label_id)
        else:
            raise TodoistError('Either label or label_id has to be provided')

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

    def update_label(self, label_id: int | str | Label, label: Label):
        """
        Update the label identified by label_id with the data from label

        Args:
            label_id: the label_id of the label to update
            label: the data to use for the update
        """
        self.labels.update(item=label_id, updated_item=label)

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
        if project:
            self.projects.delete(item=project)
        elif project_id:
            self.projects.delete(item=project_id)
        else:
            raise TodoistError('Either project or project_id has to be provided')

    def get_project(self, project_id: int | str) -> Project:
        """Get project by id

        This is convenience wrapper for TodoistAPI.projects.get_by_id(project_id)
        Args:
            project_id: the id of the project

        Returns:
            A Project instance with all project details
        """
        return self.projects.get_by_id(item_id=project_id)

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

    def update_project(self, project_id: int | str | Project, project: Project):
        """
        Update the project identified by project_id with the data from project

        Args:
            project_id: the project_id of the project to update
            project: the data to use for the update
        """
        self.projects.update(item=project_id, updated_item=project)

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
        if reminder:
            self.reminders.delete(item=reminder)
        elif reminder_id:
            self.reminders.delete(item=reminder_id)
        else:
            raise TodoistError('Either reminder or reminder_id has to be provided')

    def get_reminder(self, reminder_id: int | str) -> Reminder | None:
        """Get reminder by id

        Args:
            reminder_id: the id of the reminder

        Returns:
            A Reminder instance with all project details
        """
        return self.reminders.get_by_id(item_id=reminder_id)  # type: ignore

    def update_reminder(self, reminder_id: int | str | Reminder, reminder: Reminder):
        """
        Update the reminder identified by reminder_id with the data from reminder

        Args:
            reminder_id: the reminder_id of the reminder to update
            reminder: the data to use for the update
        """
        self.reminders.update(item=reminder_id, updated_item=reminder)

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
        if section:
            self.sections.delete(item=section)
        elif section_id:
            self.sections.delete(item=section_id)
        else:
            raise TodoistError('Either section or section_id has to be provided')

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

    def update_section(self, section_id: int | str | Section, section: Section):
        """
        Update the section identified by section_id with the data from section

        Args:
            section_id: the section_id of the section to update
            section: the data to use for the update
        """
        self.sections.update(item=section_id, updated_item=section)

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
        if task:
            self.tasks.close(item=task)
        elif task_id:
            self.tasks.close(item=task_id)
        else:
            raise TodoistError('Either task or task_id has to be provided')

    def delete_task(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
        """Delete a task

        Args:
            task_id: the id of the task to delete
            task: the Task object to delete (keyword-only argument)

        Either the task_id or the task must be provided. The task object takes priority over the task_id argument if both are provided
        """
        if task:
            self.tasks.delete(item=task)
        elif task_id:
            self.tasks.delete(item=task_id)
        else:
            raise TodoistError('Either task or task_id has to be provided')

    def get_task(self, task_id: int | str) -> Task:
        """Get task by id

        Args:
            task_id: the id of the task

        Returns:
            A Task instance with all task details
        """
        return self.tasks.get_by_id(item_id=task_id)

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

    def move_task(self, task: Task, parent: str | int | Task | None = None, section: str | int | Section | None = None,
                  project: str | int | Project | None = None) -> None:
        """
        Move task to a different parent, section or project

        One of the parameters has to be provided.

        To move an item from a section to no section, just use the project_id parameter, with the project it currently belongs to as a value.

        Args:
            task: a Task instance that you want to move
            parent: the parent under which you want to place the task
            section: the section in which you want to place the task
            project: the project in which you want to place the task
        """
        self.tasks.move(item=task, parent=parent, section=section, project=project)

    def reopen_task(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
        """Reopen a task

        Args:
            task_id: the id of the task to reopen
            task: the Task object to reopen (keyword-only argument)

        Either the task_id or the task must be provided. The task object takes priority over the task_id argument if both are provided
        """
        if task:
            self.tasks.reopen(item=task)
        elif task_id:
            self.tasks.reopen(item=task_id)
        else:
            raise TodoistError('Either task or task_id has to be provided')

    def update_task(self, task_id: int | str | Task, task: Task):
        """
        Update the label identified by task_id with the data from task

        Args:
            task_id: the task_id of the task to update
            task: the data to use for the update
        """
        self.tasks.update(item=task_id, updated_item=task)

    # endregion

    # region User methods
    def get_stats(self) -> Any:
        """Get Todoist usage statistics

        Returns:
            A dict with all user stats
        """
        return command_manager.get('completed/get_stats', self.api_key)
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
    # project_: Project = todoist_.get_project_by_pattern('Personal')  # type: ignore
    # project_ = todoist_.get_project(project_id='2198523714')
    # task_to_add = Task(content="Buy Honey", project_id="2198523714")
    # todoist_.add(task_to_add)
    # todoist_.commit()
    # todoist_.move_task(task=task_to_add, project=project_)
    # todoist_.commit()
    # print(task_to_add)
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
