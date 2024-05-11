import json
from datetime import datetime, date

from synctodoist.models.due import Due

DUE_DATE = """
{
    "date": "2016-12-01",
    "timezone": null,
    "string": "every day",
    "lang": "en",
    "is_recurring": true
}
"""

DUE_DATETIME = """
{
    "date": "2016-12-01T00:01:02",
    "timezone": null,
    "string": "every day",
    "lang": "en",
    "is_recurring": true
}
"""

DUE_NULL = """
{
    "date": null,
    "timezone": null,
    "string": "every day",
    "lang": "en",
    "is_recurring": true
}
"""


def test_due_date():
    due = Due(**json.loads(DUE_DATE))
    assert due.date == date(2016, 12, 1)


def test_due_datetime():
    due = Due(**json.loads(DUE_DATETIME))
    assert due.date == datetime(2016, 12, 1, 0, 1, 2)


def test_due_null():
    due = Due(**json.loads(DUE_NULL))
    assert due.date is None
