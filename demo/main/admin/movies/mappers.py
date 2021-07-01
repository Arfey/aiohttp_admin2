from aiohttp_admin2.mappers.generics import PostgresMapperGeneric

from ...catalog.tables import (
    movies,
    movies_actors,
    movies_genres,
)


__all__ = ['MoviesMapper', 'ActorMoviesMapper', 'GenreMoviesMapper', ]


class MoviesMapper(PostgresMapperGeneric, table=movies):
    pass


class ActorMoviesMapper(PostgresMapperGeneric, table=movies_actors):
    pass


class GenreMoviesMapper(PostgresMapperGeneric, table=movies_genres):
    pass
