import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from aiohttp_admin2.mappers.base import Mapper
from aiohttp_admin2.mappers import fields


__all__ = [
    "PostgresMapperGeneric",
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
        postgresql.ENUM: fields.ChoicesField,
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
                    field_cls=(
                        cls.FIELDS_MAPPER
                        .get(type(column.type.item_type), cls.DEFAULT_FIELD)
                    ),
                    **field_kwargs
                )
            else:
                field = field_cls(**field_kwargs)

            field.name = name
            if name not in existing_fields:
                cls._fields[name] = field
                cls._fields_cls.append(field)
