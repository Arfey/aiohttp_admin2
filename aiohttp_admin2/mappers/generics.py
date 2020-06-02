import sqlalchemy as sa
import umongo

from aiohttp_admin2.mappers.base import Mapper
from aiohttp_admin2.mappers import fields
from aiohttp_admin2.mappers.fields import mongo_fields


__all__ = [
    "PostgresMapperGeneric",
    "MongoMapperGeneric",
]


class PostgresMapperGeneric(Mapper):
    """
    This class need for generate Mapper from sqlalchemy's model.
    """

    # todo: added types
    FIELDS_MAPPER = {
        sa.Integer: fields.IntField,
        sa.Text: fields.StringField,
    }
    DEFAULT_FIELD = fields.StringField

    def __init_subclass__(cls, table: sa.Table) -> None:
        cls._fields = {}
        for name, column in table.columns.items():
            field = \
                cls.FIELDS_MAPPER.get(type(column.type), cls.DEFAULT_FIELD)()
            field.name = name
            cls._fields[name] = field


class MongoMapperGeneric(Mapper):
    """
    This class need for generate Mapper from Mongo model.
    """

    FIELDS_MAPPER = {
        umongo.fields.ObjectIdField: mongo_fields.ObjectIdField,
        umongo.fields.IntegerField: fields.IntField,
        umongo.fields.StringField: fields.StringField,
        umongo.fields.DateTimeField: fields.DateTimeField,
    }

    DEFAULT_FIELD = fields.StringField

    def __init_subclass__(cls, table: umongo.Document) -> None:
        if isinstance(table, umongo.template.MetaTemplate):
            obj_fields = (
                (key, value)
                for key, value in table.__dict__.items()
                if isinstance(value, umongo.fields.BaseField)
            )
        else:
            obj_fields = table.schema.fields.items()

        for name, column in obj_fields:
            field = \
                cls.FIELDS_MAPPER.get(type(column), cls.DEFAULT_FIELD)()
            field.name = name
            cls._fields_cls.append(field)
