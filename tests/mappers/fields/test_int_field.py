import pytest

from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.mappers import fields


class IntMapper(Mapper):
    field = fields.IntField()


class SmallIntMapper(Mapper):
    field = fields.SmallIntField()


@pytest.mark.parametrize('mapper_cls', [IntMapper, SmallIntMapper])
def test_correct_int_type(mapper_cls):
    """
    In this test we check success convert to int type.
    """
    mapper = mapper_cls({"field": 1})
    mapper.is_valid()

    assert mapper.data["field"] == 1

    mapper = mapper_cls({"field": 2})
    mapper.is_valid()

    assert mapper.data["field"] == 2

    mapper = mapper_cls({"field": -3})
    mapper.is_valid()

    assert mapper.data["field"] == -3

    mapper = mapper_cls({"field": 0})
    mapper.is_valid()

    assert mapper.data["field"] == 0

    mapper = mapper_cls({"field": 1.1})
    mapper.is_valid()

    assert mapper.data["field"] == 1


@pytest.mark.parametrize('mapper_cls', [IntMapper, SmallIntMapper])
def test_wrong_int_type(mapper_cls):
    """
    In this test we check error when we received wrong int type.
    """
    assert mapper_cls({"field": "string"}).is_valid() is False

    assert mapper_cls({"field": []}).is_valid() is False


def test_small_int_validation():
    """
    Small int value must be in range from -32_768 to 32_767. In this test we
    check that.
    """
    mapper = SmallIntMapper({"field": -32_769})
    assert not mapper.is_valid()

    mapper = SmallIntMapper({"field": 32_768})
    assert not mapper.is_valid()
