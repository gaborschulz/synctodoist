from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Project


class ProjectManager(BaseManager[Project]):
    """Project manager model"""
    model = Project

    def get_by_id(self, project_id: int | str) -> Project:  # pylint: disable=arguments-renamed
        """Get project by id

        Args:
            project_id: the id of the project

        Returns:
            A Project instance with all project details
        """
        if project := super().get_by_id(item_id=project_id):
            return project

        try:
            endpoint = self.model.Config.api_get
            if isinstance(project_id, str) and project_id.isdigit():
                project_id = int(project_id)

            data = {'project_id': project_id, 'all_data': False}
            result = command_manager.post(data, endpoint, self._api.api_key)
            project = Project(**result['project'])
            self._items.update({str(project.id): project})
            return project
        except Exception as ex:
            raise TodoistError(f'Project {project_id} not found') from ex

    def delete(self, project_id: int | str | None = None, *, project: Project | None = None) -> None:
        """Delete a project

        Args:
            project_id: the id of the project to delete
            project: the Project object to delete (keyword-only argument)

        Either the project_id or the project must be provided. The project object takes priority over the project_id argument if both are provided
        """

        if not project_id and not project:
            raise TodoistError('Either project_id or project have to be provided')

        if isinstance(project, Project):
            if not project.id:
                project_id = project.temp_id
            else:
                project_id = str(project.id)

        if isinstance(project_id, int):
            project_id = str(project_id)

        command_manager.add_command(data={'id': project_id}, command_type='project_delete')
