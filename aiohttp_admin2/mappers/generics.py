import sqlalchemy as sa

from aiohttp_admin2.mappers.base import Mapper
from aiohttp_admin2.mappers import fields


__all__ = ["PostgresMapperGeneric", ]


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
        for name, column in table.columns.items():
            field = \
                cls.FIELDS_MAPPER.get(type(column.type), cls.DEFAULT_FIELD)()
            field.name = name
            cls._fields_cls.append(field)
