from typing import Any

from synctodoist.exceptions import TodoistError
from synctodoist.managers import ProjectManager, command_manager, TaskManager, LabelManager, SectionManager, ReminderManager
from synctodoist.models import Task, Project, Label, Section, TodoistBaseModel, Reminder, Settings

CACHE_MAPPING = {x.Config.cache_label: x for x in TodoistBaseModel.__subclasses__()}
RESOURCE_TYPES = [x.Config.todoist_resource_type for x in TodoistBaseModel.__subclasses__()]


class TodoistAPI:  # pylint: disable=too-many-instance-attributes,missing-class-docstring,line-too-long
    def __init__(self, settings: Settings | None = None, **kwargs):
        """
        You can initialize TodoistAPI in two ways: either with a `Settings` object in the settings argument, or you can provide your settings as arguments to
        the initializer. These will be passed on directly to the initializer of the `Settings` object.

        The `Settings` model will try to infer your settings from environment variables, and you can configure it to use Docker secrets inside containers.
        For more details, please, check the documentation of the `Settings` model.

        Examples:
            >>> from synctodoist import TodoistAPI
            >>> api = TodoistAPI()


            or

            >>> from synctodoist import TodoistAPI
            >>> from synctodoist.models import Settings
            >>> settings = Settings(...)
            >>> api = TodoistAPI(settings=settings)

            or

            >>> from synctodoist import TodoistAPI
            >>> api = TodoistAPI(api_key="...", cache_dir="...")

        Args:
            settings: an instance of the `Settings` class
            **kwargs: keyword arguments that should be passed on to the `Settings` object. These will be passed on only if the `settings` argument is not provided.
        """
        if settings:
            self.settings = settings
        else:
            self.settings = Settings(**kwargs)

        self.synced = False
        self.projects: ProjectManager = ProjectManager(settings=self.settings)
        self.tasks: TaskManager = TaskManager(settings=self.settings)
        self.labels: LabelManager = LabelManager(settings=self.settings)
        self.sections: SectionManager = SectionManager(settings=self.settings)
        self.reminders: ReminderManager = ReminderManager(settings=self.settings)

        command_manager.settings = self.settings

    # region PRIVATE METHODS

    def _write_all_caches(self):
        for key in CACHE_MAPPING:
            target = getattr(self, key)
            target._write_cache()  # pylint: disable=protected-access

    def _read_all_caches(self):
        for key in CACHE_MAPPING:
            target = getattr(self, key)
            target._read_cache()  # pylint: disable=protected-access

    # endregion

    # region PUBLIC METHODS
    # region Global methods
    def add(self, item: TodoistBaseModel) -> None:
        """Add new item (any subclass of `TodoistBaseModel`) to Todoist

        Args:
            item: a instance of a TodoistBaseModel subclass that you would like to submit to Todoist
        """
        # type: ignore
        model = type(item)
        key = model.Config.cache_label
        model_manager = getattr(self, key)
        model_manager.add(item=item)

    def commit(self) -> Any:
        """Commit open commands to Todoist.

        Commands are processed in batches to be frugal with the request limits defined by the Todoist API (check
        [Limits](https://developer.todoist.com/sync/v9/#request-limits) in the Todoist developer documentation for more details).

        Examples:
            >>> from synctodoist import TodoistAPI
            >>> api = TodoistAPI()
            >>> api.commit()

        Raises:
            TodoistError: if the Todoist Sync API responds with an error to your request.
        """
        result = command_manager.commit()

        self.sync()
        return result

    def sync(self, full_sync: bool = False) -> bool:
        """Synchronize with Todoist API

        Examples:
            >>> from synctodoist import TodoistAPI
            >>> api = TodoistAPI()
            >>> api.sync()

        Args:
            full_sync: Set to `True` if you would like to perform a full synchronization, or `False` if you prefer a partial sync.

        Returns:
            `True` if a full sync was performed, `False` otherwise

        Raises:
            TodoistError: if the synchronization fails
        """
        if not full_sync:
            command_manager.read_sync_token()

        self._read_all_caches()

        data = {'resource_types': RESOURCE_TYPES}
        result = command_manager.post(data, 'sync')

        for key in CACHE_MAPPING:
            target = getattr(self, key)
            model = CACHE_MAPPING[key]
            # Add new items
            target._dict_update({x['id']: model(**x) for x in result[model.Config.todoist_resource_type]})  # pylint: disable=protected-access
            # Remove deleted items
            target._remove_deleted(result[model.Config.todoist_resource_type], result['full_sync'])  # pylint: disable=protected-access

        self._write_all_caches()
        command_manager.write_sync_token()

        self.synced = True
        return result['full_sync']  # type: ignore

    # endregion

    # region Label methods
    def add_label(self, label: Label) -> None:
        """Add new label to todoist.

        Note:
            This is a convenience wrapper for `TodoistAPI.add(item=label)`.

        Args:
            label: a Label instance to add to Todoist
        """
        self.add(label)

    def delete_label(self, label_id: int | str | None = None, *, label: Label | None = None) -> None:
        """Delete a label

        Important:
            Either the `label_id` or the `label` must be provided. The `label` object takes priority over the `label_id` argument if both are provided.

        Args:
            label_id: the id of the label to delete
            label: the Label object to delete (keyword-only argument)

        Raises:
            TodoistError: if neither `label_id` nor `label` are provided.
        """
        if label:
            self.labels.delete(item=label)
        elif label_id:
            self.labels.delete(item=label_id)
        else:
            raise TodoistError('Either label or label_id has to be provided')

    def find_label(self, pattern: str, return_all: bool = False) -> Label | list[Label]:
        """Find labels based on a regex pattern.

        Important:
            You have to run the `.sync()` method first for this to work

        Args:
            pattern: the regex pattern against which the label's name is matched
            return_all: returns only the first matching item if set to False (default), otherwise returns all matching items as a list

        Returns:
            A `Label` instance containing the label details, or a list of `Label` instances if `return_all` was set to `True`

        Raises:
            TodoistError: if `return_all=False` and no matching value is found
        """
        return self.labels.find(pattern=pattern, field='name', return_all=return_all)

    def get_label(self, label_id: int | str) -> Label | None:
        """Get label by id

        Note:
            This is convenience wrapper for TodoistAPI.labels.get(label_id)

        Args:
            label_id: the id of the label

        Returns:
            A `Label` instance with all project details

        Raises:
            TodoistError: if `label_id` is not found
        """
        return self.labels.get(item_id=label_id)  # type: ignore

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

        Note:
            This is a convenience wrapper for `TodoistAPI.add(item=project)`.

        Args:
            project: a Project instance to add to Todoist
        """
        self.add(project)

    def delete_project(self, project_id: int | str | None = None, *, project: Project | None = None) -> None:
        """Delete a project

        Important:
            Either the `project_id` or the `project` must be provided. The `project` object takes priority over the `project_id` argument if both are provided.

        Args:
            project_id: the id of the project to delete
            project: the Project object to delete (keyword-only argument)

        Raises:
            TodoistError: if neither `project_id` nor `project` are provided.
        """
        if project:
            self.projects.delete(item=project)
        elif project_id:
            self.projects.delete(item=project_id)
        else:
            raise TodoistError('Either project or project_id has to be provided')

    def find_project(self, pattern: str, return_all: bool = False) -> Project | list[Project]:
        """Find projects based on a regex pattern

        Important:
            You have to run the `.sync()` method first for this to work

        Args:
            pattern: the regex pattern against which the project's name is matched
            return_all: returns only the first matching item if set to False (default), otherwise returns all matching items as a list

        Returns:
            A `Project` instance containing the project details, or a list of `Project` instances if `return_all` was set to `True`

        Raises:
            TodoistError: if `return_all=False` and no matching value is found
        """
        return self.projects.find(pattern=pattern, field='name', return_all=return_all)

    def get_project(self, project_id: int | str) -> Project:
        """Get project by id

        Note:
            This is convenience wrapper for TodoistAPI.projects.get(project_id)

        Args:
            project_id: the id of the project

        Returns:
            A `Project` instance with all project details

        Raises:
            TodoistError: if `project_id` is not found
        """
        return self.projects.get(item_id=project_id)

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

        Note:
            This is a convenience wrapper for `TodoistAPI.add(item=reminder)`.

        Args:
            reminder: a Reminder instance to add to Todoist
        """
        self.add(reminder)

    def delete_reminder(self, reminder_id: int | str | None = None, *, reminder: Reminder | None = None) -> None:
        """Delete a reminder

        Important:
            Either the `reminder_id` or the `reminder` must be provided. The `reminder` object takes priority over the `reminder_id` argument if both are provided.

        Args:
            reminder_id: the id of the reminder to delete
            reminder: the Reminder object to delete (keyword-only argument)

        Raises:
            TodoistError: if neither `reminder_id` nor `reminder` are provided.
        """
        if reminder:
            self.reminders.delete(item=reminder)
        elif reminder_id:
            self.reminders.delete(item=reminder_id)
        else:
            raise TodoistError('Either reminder or reminder_id has to be provided')

    def get_reminder(self, reminder_id: int | str) -> Reminder | None:
        """Get reminder by id

        Note:
            This is convenience wrapper for TodoistAPI.reminders.get(reminder_id)

        Args:
            reminder_id: the id of the reminder

        Returns:
            A Reminder instance with all project details

        Raises:
            TodoistError: if `reminder_id` is not found
        """
        return self.reminders.get(item_id=reminder_id)  # type: ignore

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

        Note:
            This is a convenience wrapper for `TodoistAPI.add(item=section)`.

        Args:
            section: a `Section` instance to add to Todoist
        """
        self.add(section)

    def delete_section(self, section_id: int | str | None = None, *, section: Section | None = None) -> None:
        """Delete a section

        Important:
            Either the `section_id` or the `section` must be provided. The `section` object takes priority over the `section_id` argument if both are provided.

        Args:
            section_id: the id of the section to delete
            section: the Section object to delete (keyword-only argument)

        Raises:
            TodoistError: if neither `section_id` nor `section` are provided.
        """
        if section:
            self.sections.delete(item=section)
        elif section_id:
            self.sections.delete(item=section_id)
        else:
            raise TodoistError('Either section or section_id has to be provided')

    def find_section(self, pattern: str, return_all: bool = False) -> Section | list[Section]:
        """Find sections based on a regex pattern.

        Important:
            You have to run the `.sync()` method first for this to work

        Args:
            pattern: the regex pattern against which the section's name is matched
            return_all: returns only the first matching item if set to False (default), otherwise returns all matching items as a list

        Returns:
            A `Section` instance containing the section details, or a list of `Section` instances if `return_all` was set to `True`

        Raises:
            TodoistError: if `return_all=False` and no matching value is found
        """
        return self.sections.find(pattern=pattern, field='name', return_all=return_all)

    def get_section(self, section_id: int | str) -> Section | None:
        """Get section by id

        Note:
            This is convenience wrapper for TodoistAPI.sections.get(project_id)

        Args:
            section_id: the id of the section

        Returns:
            A `Section` instance with all project details

        Raises:
            TodoistError: if `section_id` is not found
        """
        return self.sections.get(item_id=section_id)

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

        Note:
            This is a convenience wrapper for `TodoistAPI.add(item=task)`.

        Args:
            task: a Task instance to add to Todoist
        """
        self.add(task)

    def close_task(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
        """Complete a task

        Important:
            Either the `task_id` or the `task` must be provided. The `task` object takes priority over the `task_id` argument if both are provided. `task` has
            to be provided as a keyword argument.

        Args:
            task_id: the id of the task to close
            task: the Task object to close (keyword-only argument)

        Raises:
            TodoistError: if neither `task_id` nor `task` are provided.
        """
        if task:
            self.tasks.close(item=task)
        elif task_id:
            self.tasks.close(item=task_id)
        else:
            raise TodoistError('Either task or task_id has to be provided')

    def delete_task(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
        """Delete a task

        Important:
            Either the `task_id` or the `task` must be provided. The `task` object takes priority over the `task_id` argument if both are provided.

        Args:
            task_id: the id of the task to delete
            task: the Task object to delete (keyword-only argument)

        Raises:
            TodoistError: if neither `task_id` nor `task` are provided.
        """
        if task:
            self.tasks.delete(item=task)
        elif task_id:
            self.tasks.delete(item=task_id)
        else:
            raise TodoistError('Either task or task_id has to be provided')

    def find_task(self, pattern: str, return_all: bool = False) -> Task | list[Task]:
        """Find tasks based on a regex pattern.

        Important:
            You have to run the `.sync()` method first for this to work

        Args:
            pattern: the regex pattern against which the task's content is matched
            return_all: returns only the first matching item if set to False (default), otherwise returns all matching items as a list

        Returns:
            A `Task` instance containing the task details, or a list of `Task` instances if `return_all` was set to `True`

        Raises:
            TodoistError: if `return_all=False` and no matching value is found
        """
        return self.tasks.find(pattern=pattern, field='content', return_all=return_all)

    def get_task(self, task_id: int | str) -> Task:
        """Get task by id

        Note:
            This is convenience wrapper for TodoistAPI.tasks.get(project_id)

        Args:
            task_id: the id of the task

        Returns:
            A Task instance with all task details

        Raises:
            TodoistError: if `task_id` is not found
        """
        return self.tasks.get(item_id=task_id)

    def move_task(self, task: Task, parent: str | int | Task | None = None, section: str | int | Section | None = None,
                  project: str | int | Project | None = None) -> None:
        """
        Move task to a different parent, section or project

        Important:
            One of the parameters has to be provided.

        To move an item from a section to no section, just use the project_id parameter, with the project it currently belongs to as a value.

        Args:
            task: a Task instance that you want to move
            parent: the parent under which you want to place the task
            section: the section in which you want to place the task
            project: the project in which you want to place the task

        Raises:
            TodoistError: if neither `parent`, `section` nor `project` are provided.
        """
        self.tasks.move(item=task, parent=parent, section=section, project=project)

    def reopen_task(self, task_id: int | str | None = None, *, task: Task | None = None) -> None:
        """Reopen a task

        Important:
            Either the `task_id` or the `task` must be provided. The `task` object takes priority over the `task_id` argument if both are provided. `task` has
            to be provided as a keyword argument.

        Args:
            task_id: the id of the task to close
            task: the Task object to close (keyword-only argument)

        Raises:
            TodoistError: if neither `task_id` nor `task` are provided.
        """
        if task:
            self.tasks.reopen(item=task)
        elif task_id:
            self.tasks.reopen(item=task_id)
        else:
            raise TodoistError('Either task or task_id has to be provided')

    def update_task(self, task_id: int | str | Task, task: Task):
        """
        Update the label identified by `task_id` with the data from `task`

        Args:
            task_id: the task_id of the task to update
            task: the data to use for the update
        """
        self.tasks.update(item=task_id, updated_item=task)

    # endregion

    # region User methods
    def get_stats(self) -> dict:
        """Get Todoist usage statistics

        Returns:
            A dict with all user stats
        """
        return command_manager.get('completed/get_stats')  # type: ignore
    # endregion
    # endregion


if __name__ == '__main__':  # pragma: no cover
    settings_ = Settings(_env_file='../.env')
    todoist_ = TodoistAPI(settings=settings_)
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
