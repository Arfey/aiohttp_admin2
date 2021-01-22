from aiohttp_admin2.mappers.generics import PostgresMapperGeneric

from ...catalog.tables import (
    movies,
    movies_actors,
)


__all__ = ['MoviesMapper', 'ActorMoviesMapper', ]


class MoviesMapper(PostgresMapperGeneric, table=movies):
    pass


class ActorMoviesMapper(PostgresMapperGeneric, table=movies_actors):
    pass
