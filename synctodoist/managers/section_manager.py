from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Section


class SectionManager(BaseManager[Section]):
    """Section manager"""
    model = Section

    def delete(self, section_id: int | str | None = None, *, section: Section | None = None) -> None:
        """Delete a section

        Args:
            section_id: the id of the section to delete
            section: the Section object to delete (keyword-only argument)

        Either the section_id or the section must be provided. The section object takes priority over the section_id argument if both are provided
        """

        if not section_id and not section:
            raise TodoistError('Either section_id or section have to be provided')

        if isinstance(section, Section):
            if not section.id:
                section_id = section.temp_id
            else:
                section_id = str(section.id)

        if isinstance(section_id, int):
            section_id = str(section_id)

        command_manager.add_command(data={'id': section_id}, command_type='section_delete')
