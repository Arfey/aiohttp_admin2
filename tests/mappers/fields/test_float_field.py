from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.mappers import fields


class FloatMapper(Mapper):
    field = fields.FloatField()


def test_correct_float_type():
    """
    In this test we check success convert to float type.
    """
    mapper = FloatMapper({"field": 1})
    mapper.is_valid()

    assert mapper.data["field"] == 1.0

    mapper = FloatMapper({"field": 2})
    mapper.is_valid()

    assert mapper.data["field"] == 2.0

    mapper = FloatMapper({"field": -3})
    mapper.is_valid()

    assert mapper.data["field"] == -3.0

    mapper = FloatMapper({"field": 0})
    mapper.is_valid()

    assert mapper.data["field"] == 0.0


def test_wrong_float_type():
    """
    In this test we check error when we received wrong float type.
    """
    assert FloatMapper({"field": "string"}).is_valid() is False

    assert FloatMapper({"field": []}).is_valid() is False
