# pylint: disable-all
import pytest
from pydantic import ValidationError

from synctodoist.models import TodoistBaseModel


def test_refresh():
    model = TodoistBaseModel(id='1')

    with pytest.raises(ValidationError):
        model.refresh(is_deleted='INVALID_VALUE')
