import sqlalchemy as sa
import umongo

from marshmallow import EXCLUDE
from marshmallow.exceptions import ValidationError as MarshmallowValidationErr
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

    FIELDS_MAPPER = {
        sa.Integer: fields.IntField,
        sa.BigInteger: fields.IntField,
        sa.SmallInteger: fields.SmallIntField,
        sa.Float: fields.FloatField,
        sa.String: fields.StringField,
        sa.Text: fields.LongStringField,
        sa.Enum: fields.ChoicesField,
        sa.Boolean: fields.BooleanField,
        sa.ARRAY: fields.ArrayField,
        sa.DateTime: fields.DateTimeField,
        sa.Date: fields.DateField,
        sa.JSON: fields.JsonField,
    }
    DEFAULT_FIELD = fields.StringField

    def __init_subclass__(cls, table: sa.Table) -> None:
        super().__init_subclass__()
        cls._fields = {}

        existing_fields = [field.name for field in cls._fields_cls]

        for name, column in table.columns.items():
            field_cls = \
                cls.FIELDS_MAPPER.get(type(column.type), cls.DEFAULT_FIELD)

            max_length = hasattr(column.type, 'length') and column.type.length
            field_kwargs = {
                "max_length": max_length,
                "required": not column.nullable,
                "primary_key": column.primary_key,
            }

            if field_cls is fields.ChoicesField:
                field = fields.ChoicesField(
                    choices=[(n, n) for n in column.type.enums],
                    **field_kwargs
                )
            elif field_cls is fields.ArrayField:
                field = field_cls(
                    field_cls=cls.FIELDS_MAPPER
                        .get(type(column.type.item_type), cls.DEFAULT_FIELD),
                    **field_kwargs
                )
            else:
                field = field_cls(**field_kwargs)

            field.name = name
            if name not in existing_fields:
                cls._fields[name] = field
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
        umongo.fields.List: fields.ArrayField,
    }

    DEFAULT_FIELD = fields.StringField

    def __init_subclass__(cls, table: umongo.Document) -> None:
        cls._fields = {}
        cls.table = table

        existing_fields = [field.name for field in cls._fields_cls]

        for name, column in table.schema.fields.items():
            field = \
                cls.FIELDS_MAPPER.get(type(column), cls.DEFAULT_FIELD)()
            field.name = name
            if name not in existing_fields:
                cls._fields_cls.append(field)
                cls._fields[name] = field

    def validation(self):
        """
        In the current method we cover marshmallow validation. We create/update
        instances via umongo which use marshmallow validation for it. We can't
        to copy all validation from marshmallow to our mapper because user can
        to set custom validation. So we just check twice that data is valid for
        the our mapper and for the marshmallow schema.
        """
        is_valid = True
        errors = {}

        try:
            # mapper may have additional fields which are not specify in the
            # schema so we need to skip validation of fields which are not
            # exist in the schema
            self.table.schema.as_marshmallow_schema()().load(
                self.raw_data,
                unknown=EXCLUDE,
            )
        except MarshmallowValidationErr as e:
            errors = e.messages

        # validation for each field
        for f in self.fields.values():
            if errors.get(f.name):
                f.errors.append(errors.get(f.name)[0])
                is_valid = False

        if not is_valid:
            raise ValidationError
