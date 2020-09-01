import sqlalchemy as sa
import umongo

from aiohttp_admin2.mappers.base import Mapper
from aiohttp_admin2.mappers import fields
from aiohttp_admin2.mappers.fields import mongo_fields
from aiohttp_admin2.mappers.exceptions import ValidationError


__all__ = [
    "PostgresMapperGeneric",
    "MongoMapperGeneric",
]


class PostgresMapperGeneric(Mapper):
    """
    This class need for generate Mapper from sqlAlchemy's model.
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

        # todo: add tests
        if not cls._fields_cls:
            cls._fields_cls = cls._fields.values()
        else:
            existing_fields = [field.name for field in cls._fields_cls]

            for name, field in cls._fields.items():
                if name not in existing_fields:
                    cls._fields_cls.append(field)


class MongoMapperGeneric(Mapper):
    """
    This class need for generate Mapper from Mongo model.
    """
    table: umongo.Document

    FIELDS_MAPPER = {
        umongo.fields.ObjectIdField: mongo_fields.ObjectIdField,
        umongo.fields.IntegerField: fields.IntField,
        umongo.fields.StringField: fields.StringField,
        umongo.fields.DateTimeField: fields.DateTimeField,
    }

    DEFAULT_FIELD = fields.StringField

    def __init_subclass__(cls, table: umongo.Document) -> None:
        cls.table = table
        obj_fields = table.schema.fields.items()

        for name, column in obj_fields:
            field = \
                cls.FIELDS_MAPPER.get(type(column), cls.DEFAULT_FIELD)()
            field.name = name
            cls._fields_cls.append(field)

    def validation(self):
        """
        In current method we cover marshmallow validation.
        """
        is_valid = True

        errors = self.table\
            .schema\
            .as_marshmallow_schema()()\
            .load(self.raw_data)\
            .errors

        # validation for each field
        for f in self.fields.values():
            if not f.error and errors.get(f.name):
                # todo: move to list of errors
                f.error = errors.get(f.name)[0]
                is_valid = False

        # validation connected with schema or field relationship
        if errors.get('_schema') and not self.error:
            self.error = errors.get('_schema')[0]
            is_valid = False

        if not is_valid:
            raise ValidationError
