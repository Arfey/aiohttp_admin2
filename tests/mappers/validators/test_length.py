"""
In this file we cower corrected work of `length` validator.

    1. If we don't have a parameterized validator, do nothing
    2. If value more than max_value then raise an error
    3. If value less than max_value then all is fine
    4. If value less than min_value then raise an error
    5. If value more than min_value then all is fine
    6. Corrected usage with all specified parameters (min and max)
"""
import pytest

from aiohttp_admin2.mappers.validators.length import length
from aiohttp_admin2.mappers.exceptions import ValidationError


def test_without_params():
    """
    1. If we don't have a parameterized validator, do nothing
    """
    length()(5)


def test_more_than_max_value():
    """
    2. If value more than max_value then raise an error
    """
    with pytest.raises(ValidationError):
        length(max_value=1)([1, 2])


def test_less_than_max_value():
    """
    3. If value less than max_value then all is fine
    """
    length(max_value=2)([1, 2])
    length(max_value=2)([1])


def test_less_than_min_value():
    """
    4. If value less than min_value then raise an error
    """
    with pytest.raises(ValidationError):
        length(min_value=1)([])


def test_more_than_min_value():
    """
    5. If value more than min_value then all is fine
    """
    length(min_value=1)([1, 2])
    length(min_value=1)([1])


def test_all_params():
    """
    6. Corrected usage with all specified parameters (min and max)
    """
    length(min_value=1, max_value=3)([1, 2])

    with pytest.raises(ValidationError):
        length(min_value=1, max_value=3)([])

    with pytest.raises(ValidationError):
        length(min_value=1, max_value=3)([1, 2, 3, 4])
