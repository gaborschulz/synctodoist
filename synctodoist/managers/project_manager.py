from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Project


class ProjectManager(BaseManager):
    """Project manager model"""
    model = Project

    def get_by_id(self, project_id: int | str) -> Project:
        """Get project by id

        Args:
            project_id: the id of the project

        Returns:
            A Project instance with all project details
        """
        if project := super().get_by_id(item_id=project_id):
            return project  # type: ignore

        try:
            endpoint = self.model.Config.api_get
            if isinstance(project_id, str):
                project_id = int(project_id)

            data = {'project_id': project_id, 'all_data': False}
            result = command_manager.post(data, endpoint, self._api.api_key)
            project = Project(**result['project'])
            self._items.update({project.id: project})  # type: ignore
            return project
        except Exception as ex:
            raise TodoistError(f'Project {project_id} not found') from ex
