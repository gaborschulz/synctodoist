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
