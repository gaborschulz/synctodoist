from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Project


class ProjectManager(BaseManager[Project]):
    """Project manager model"""
    model = Project

    def get(self, item_id: int | str) -> Project:  # pylint: disable=arguments-renamed
        """Get project by id

        Args:
            item_id: the id of the project

        Returns:
            A Project instance with all project details
        """
        if project := super().get(item_id=item_id):
            return project

        try:
            endpoint = self.model.Config.api_get
            if isinstance(item_id, str) and item_id.isdigit():
                item_id = int(item_id)

            data = {'project_id': item_id, 'all_data': False}
            result = command_manager.post(data, endpoint)
            project = Project(**result['project'])
            self._items.update({str(project.id): project})
            return project
        except Exception as ex:
            raise TodoistError(f'Project {item_id} not found') from ex
