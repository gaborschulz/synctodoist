# pylint: disable-all
from pathlib import Path

from synctodoist import TodoistAPI
from synctodoist.managers import command_manager
from synctodoist.models import Settings


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
    settings = Settings(cache_dir=Path.home())
    api = TodoistAPI(settings=settings)
    assert command_manager.settings.cache_dir == Path.home()


def test_settings_populated_from_kwargs():
    api = TodoistAPI(api_key='Test', cache_dir=Path.home())
    assert api.settings.api_key == 'Test'
    assert api.settings.cache_dir == Path.home()
