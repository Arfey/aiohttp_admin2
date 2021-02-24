from aiohttp_admin2.controllers.postgres_controller import PostgresController

from .mappers import (
    ActorMoviesMapper,
    MoviesMapper,
    GenreMoviesMapper,
)
from ..actors.controllers import ActorController
from ..genres.controllers import GenresController
from ..injectors import postgres_injector
from ...catalog.tables import (
    movies,
    movies_actors,
    movies_genres,
)


__all__ = ['MoviesController', 'ActorMovieController', 'GenreMovieController', ]


@postgres_injector.inject
class MoviesController(PostgresController):
    table = movies
    mapper = MoviesMapper
    name = 'movies'
    per_page = 10
    inline_fields = [
        'poster', 'title', 'status', 'release_date', 'vote_average',
    ]

    async def poster_field(self, obj):
        return f'<img ' \
               f'src="https://image.tmdb.org/t/p/w200/{obj.poster_path}"' \
               f'width="100">'

    poster_field.is_safe = True


@postgres_injector.inject
class ActorMovieController(PostgresController):
    table = movies_actors
    mapper = ActorMoviesMapper
    inline_fields = [
        'id', 'photo', 'actor_id', 'actor_name', 'character', 'order'
    ]
    order_by = 'order'

    per_page = 10

    foreign_keys = {
        'movie_id': MoviesController,
        'actor_id': ActorController,
    }

    async def photo_field(self, obj):
        return f'<img ' \
               f'src="https://image.tmdb.org/t/p/w200/' \
               f'{obj._relations.get("actor_id").url}"' \
               f'width="100">'

    photo_field.is_safe = True

    async def actor_name_field(self, obj):
        return obj._relations.get('actor_id').name


@postgres_injector.inject
class GenreMovieController(PostgresController):
    table = movies_genres
    mapper = GenreMoviesMapper
    inline_fields = ['id', 'name', ]

    async def name_field(self, obj) -> str:
        return obj._relations.get('genre_id').name


    per_page = 10

    foreign_keys = {
        'movie_id': MoviesController,
        'genre_id': GenresController,
    }
