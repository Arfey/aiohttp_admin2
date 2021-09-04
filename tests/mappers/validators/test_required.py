import pytest

from aiohttp_admin2.mappers.validators.required import required
from aiohttp_admin2.mappers.exceptions import ValidationError


def test_required():
    with pytest.raises(ValidationError):
        required('')

    with pytest.raises(ValidationError):
        required(None)

    required(0)
    required(False)
    required('this')
