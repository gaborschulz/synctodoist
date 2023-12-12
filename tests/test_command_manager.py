# pylint: disable-all
import os

import pytest
from dotenv import load_dotenv

from synctodoist.exceptions import TodoistError
from synctodoist.managers import command_manager

load_dotenv('../.env')
API_KEY = os.environ.get('TODOIST_API')


def test_invalid_command_commit_error():
    command_manager.add_command(data={'id': 'INVALID'}, command_type='INVALID')
    assert len(command_manager.commands) > 0

    with pytest.raises(TodoistError):
        command_manager.commit()

    command_manager.commands.clear()
