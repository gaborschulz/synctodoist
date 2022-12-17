from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager
from synctodoist.managers.base_manager import BaseManager
from synctodoist.models import Label


class LabelManager(BaseManager[Label]):
    """Project manager"""
    model = Label

    def delete(self, label_id: int | str | None = None, *, label: Label | None = None) -> None:
        """Delete a label

        Args:
            label_id: the id of the label to delete
            label: the Label object to delete (keyword-only argument)

        Either the label_id or the label must be provided. The label object takes priority over the label_id argument if both are provided
        """

        if not label_id and not label:
            raise TodoistError('Either label_id or label have to be provided')

        if isinstance(label, Label):
            if not label.id:
                label_id = label.temp_id
            else:
                label_id = str(label.id)

        if isinstance(label_id, int):
            label_id = str(label_id)

        command_manager.add_command(data={'id': label_id}, command_type='label_delete')
