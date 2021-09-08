import datetime

import pytest

from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.mappers import fields


class ArrayMapper(Mapper):
    field = fields.ArrayField(field_cls=fields.IntField)


@pytest.mark.parametrize('item_cls, input_data, output_data', [
    (fields.StringField, '[1, 2, 3]', ['1', '2', '3']),
    (fields.StringField, [1, 2, 3], ['1', '2', '3']),
    (
        fields.DateTimeField,
        '["2021-09-05T00:14:49.466639"]',
        [datetime.datetime(2021, 9, 5, 0, 14, 49, 466639)],
    ),
    (
        fields.DateTimeField,
        [datetime.datetime(2021, 9, 5, 0, 14, 49, 466639)],
        [datetime.datetime(2021, 9, 5, 0, 14, 49, 466639)],
    ),
    (fields.DateField, '["2021-09-05"]', [datetime.date(2021, 9, 5)]),
    (
        fields.DateField,
        [datetime.date(2021, 9, 5)],
        [datetime.date(2021, 9, 5)]
    ),
    (fields.IntField, '[1, 2, 3]', [1, 2, 3]),
    (fields.IntField, [1, 2, 3], [1, 2, 3]),
    (fields.IntField, '[1, 2, 3]', [1, 2, 3]),
    (fields.FloatField, '[1.1, 2, 3]', [1.1, 2.0, 3.0]),
    (fields.FloatField, [1.1, 2, 3], [1.1, 2.0, 3.0]),
    (fields.BooleanField, '["t", "f", "False"]', [True, False, False]),
    (fields.BooleanField, [True, False, "False"], [True, False, False]),
])
def test_different_types_of_items(item_cls, input_data, output_data):
    """
    In this test we check corrected converting items of array of different
    types.
    """
    class InnerMapper(Mapper):
        field = fields.ArrayField(field_cls=item_cls)

    mapper = InnerMapper({'field': input_data})

    mapper.is_valid()
    assert mapper.data['field'] == output_data


def test_error_with_wrong_type():
    """
    In current test we check error if received wrong type
    """
    assert not ArrayMapper({'field': 'string'}).is_valid()
    assert not ArrayMapper({'field': 1}).is_valid()
    assert not ArrayMapper({'field': '["str", "str"]'}).is_valid()
    assert not ArrayMapper({'field': ['str', 'str']}).is_valid()


def test_length_validation():
    """
    Test corrected work of mix/max_length validation. If array less than
    min_length or greater than max_length then we must to receive an error.
    """

    class InnerArrayMapperWithMax(Mapper):
        field = fields.ArrayField(field_cls=fields.IntField, max_length=1)

    assert InnerArrayMapperWithMax({"field": []}).is_valid()
    assert InnerArrayMapperWithMax({"field": [1]}).is_valid()
    assert not InnerArrayMapperWithMax({"field": [1, 2]}).is_valid()

    class InnerArrayMapperWithMin(Mapper):
        field = fields.ArrayField(field_cls=fields.IntField, min_length=1)

    assert InnerArrayMapperWithMin({"field": [1, 2]}).is_valid()
    assert InnerArrayMapperWithMin({"field": [1]}).is_valid()
    assert not InnerArrayMapperWithMin({"field": []}).is_valid()

    class InnerArrayMapperFull(Mapper):
        field = fields\
            .ArrayField(field_cls=fields.IntField, min_length=1, max_length=2)

    assert InnerArrayMapperFull({"field": [1, 2]}).is_valid()
    assert InnerArrayMapperFull({"field": [1]}).is_valid()
    assert not InnerArrayMapperFull({"field": []}).is_valid()
    assert not InnerArrayMapperFull({"field": [1, 2, 3]}).is_valid()
