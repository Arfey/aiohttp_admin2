from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
from aiohttp_admin2.mappers import fields

from .validators import validate_short_name
from ...catalog.tables import genres

__all__ = ["GenresMapper", ]


class GenresMapper(PostgresMapperGeneric, table=genres):
    name = fields.StringField(required=True, validators=[validate_short_name])
