from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.mappers import fields


class BooleanMapper(Mapper):
    field = fields.BooleanField()


def test_validation_from_string():
    """
    In this test we check that if mapper receive string value than it try to
    convert it in right python's format.
    """
    # '0' -> False
    mapper = BooleanMapper({"field": '0'})
    assert mapper.is_valid()
    assert mapper.data['field'] is False

    # 'false' -> False
    mapper = BooleanMapper({"field": 'false'})
    assert mapper.is_valid()
    assert mapper.data['field'] is False

    # 'f' -> False
    mapper = BooleanMapper({"field": 'f'})
    assert mapper.is_valid()
    assert mapper.data['field'] is False

    # '' -> False
    mapper = BooleanMapper({"field": ''})
    assert mapper.is_valid()
    assert mapper.data['field'] is False

    # 'none' -> False
    mapper = BooleanMapper({"field": 'none'})
    assert mapper.is_valid()
    assert mapper.data['field'] is False

    # False -> False
    mapper = BooleanMapper({"field": False})
    assert mapper.is_valid()
    assert mapper.data['field'] is False

    # all other is True
    mapper = BooleanMapper({"field": 'True'})
    assert mapper.is_valid()
    assert mapper.data['field'] is True

    # True other is True
    mapper = BooleanMapper({"field": True})
    assert mapper.is_valid()
    assert mapper.data['field'] is True

