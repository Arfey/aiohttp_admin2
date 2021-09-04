import datetime

from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.mappers import fields


class DateMapper(Mapper):
    field = fields.DateField()


class DateTimeMapper(Mapper):
    field = fields.DateTimeField()


def test_correct_date_type():
    """In this test we cover success convert string to date type"""
    mapper = DateMapper({"field": "2021-07-12"})
    assert mapper.is_valid()
    assert mapper.data['field'] == datetime.date(2021, 7, 12)


def test_wrong_date_type():
    """In this test we cover case with wrong date type"""
    assert not DateMapper({"field": 1}).is_valid()
    assert not DateMapper({"field": 'ddd'}).is_valid()


def test_default_date_str_value():
    """In this test we check that we can specify default value as str"""

    class DateMapperStr(Mapper):
        field = fields.DateField(default="2021-07-12")

    mapper = DateMapperStr({})
    assert mapper.is_valid()
    assert mapper.data['field'] == datetime.date(2021, 7, 12)


def test_default_date_date_object_value():
    """In this test we check that we can specify default value as date"""

    class DateMapperStr(Mapper):
        field = fields.DateField(default=datetime.date(2021, 7, 12))

    mapper = DateMapperStr({})
    assert mapper.is_valid()
    assert mapper.data['field'] == datetime.date(2021, 7, 12)


def test_correct_datetime_type():
    """In this test we cover success convert string to datetime type"""
    mapper = DateTimeMapper({"field": "2021-07-12 09:44:49"})
    assert mapper.is_valid()
    assert mapper.data['field'] == datetime.datetime(2021, 7, 12, 9, 44, 49)


def test_wrong_datetime_type():
    """In this test we cover case with wrong datetime type"""
    assert not DateTimeMapper({"field": 1}).is_valid()
    assert not DateTimeMapper({"field": 'ddd'}).is_valid()


def test_default_datetime_str_value():
    """In this test we check that we can specify default value as str"""

    class DateTimeMapperStr(Mapper):
        field = fields.DateTimeField(default="2021-07-12 09:44:49")

    mapper = DateTimeMapperStr({})
    assert mapper.is_valid()
    assert mapper.data['field'] == datetime.datetime(2021, 7, 12, 9, 44, 49)


def test_default_datetime_datetime_object_value():
    """In this test we check that we can specify default value as datetime"""

    class DateTimeMapperStr(Mapper):
        field = fields\
            .DateTimeField(default=datetime.datetime(2021, 7, 12, 9, 44, 49))

    mapper = DateTimeMapperStr({})
    assert mapper.is_valid()
    assert mapper.data['field'] == datetime.datetime(2021, 7, 12, 9, 44, 49)
