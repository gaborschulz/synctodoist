# pylint: disable-all
import os
from pathlib import Path

from dotenv import load_dotenv

from synctodoist import TodoistAPI
from synctodoist.managers import command_manager

load_dotenv()
API_KEY = os.environ.get('TODOIST_API')


def test_sync(todoist):
    assert not todoist.synced
    todoist.sync()
    assert todoist.synced
    assert len(todoist.projects) > 0
    assert len(todoist.tasks) > 0
    assert len(todoist.labels) > 0
    assert len(todoist.sections) > 0


def test_get_stats(todoist):
    stats = todoist.get_stats()
    assert 'karma' in stats


def test_sync_custom_cache_path():
    api = TodoistAPI(api_key=API_KEY, cache_dir=Path.home())
    assert command_manager.cache_dir == Path.home()
