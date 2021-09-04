import pytest

from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.mappers import fields


class StringMapper(Mapper):
    field = fields.StringField()


class LongStringFieldMapper(Mapper):
    field = fields.LongStringField()


@pytest.mark.parametrize('mapper_cls', [StringMapper, LongStringFieldMapper])
def test_correct_str_type(mapper_cls):
    """
    In this test we check success convert to str type.
    """
    mapper = mapper_cls({"field": 1})
    mapper.is_valid()

    assert mapper.data["field"] == '1'

    mapper = mapper_cls({"field": False})
    mapper.is_valid()

    assert mapper.data["field"] == "False"

    mapper = mapper_cls({"field": -3})
    mapper.is_valid()

    assert mapper.data["field"] == "-3"

    mapper = mapper_cls({"field": 0.0})
    mapper.is_valid()

    assert mapper.data["field"] == "0.0"

    mapper = mapper_cls({"field": "string"})
    mapper.is_valid()

    assert mapper.data["field"] == "string"

    mapper = mapper_cls({"field": ""})
    mapper.is_valid()

    assert mapper.data["field"] == ""

    mapper = mapper_cls({"field": [1, 2]})
    mapper.is_valid()

    assert mapper.data["field"] == "[1, 2]"
