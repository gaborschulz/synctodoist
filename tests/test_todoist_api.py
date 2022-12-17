# pylint: disable-all
import os

from dotenv import load_dotenv

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
