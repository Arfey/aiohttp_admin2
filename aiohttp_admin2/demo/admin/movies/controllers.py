from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.controllers.relations import ToManyRelation
from aiohttp_admin2.controllers.relations import ToOneRelation
from .mappers import (
    ActorMoviesMapper,
    MoviesMapper,
    GenreMoviesMapper,
)
from ..actors.controllers import ActorController
from ..genres.controllers import GenresController
from ..images.controller import ImageController
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
    autocomplete_search_fields = ['title', ]

    async def poster_field(self, obj):
        return f'<img ' \
               f'src="https://image.tmdb.org/t/p/w200/{obj.data.poster_path}"'\
               f'width="100">'

    poster_field.is_safe = True

    relations_to_many = [
        ToManyRelation(
            name='Actors',
            left_table_pk='movie_id',
            right_table_pk='actor_id',
            relation_controller=lambda: ActorMovieController
        ),
        ToManyRelation(
            name='Genres',
            left_table_pk='movie_id',
            right_table_pk='genre_id',
            relation_controller=lambda: GenreMovieController
        ),
        ToManyRelation(
            name='Images',
            left_table_pk='movie_id',
            right_table_pk='id',
            relation_controller=ImageController
        ),
    ]

    async def get_object_name(self, obj):
        return f"{obj.get_pk()} - {obj.data.title}"


@postgres_injector.inject
class ActorMovieController(PostgresController):
    table = movies_actors
    mapper = ActorMoviesMapper
    inline_fields = [
        'id', 'photo', 'actor_id', 'actor_name', 'character', 'order'
    ]
    autocomplete_search_fields = ['name', ]
    exclude_update_fields = ['actor_id', 'movie_id', 'id', ]
    order_by = 'order'

    per_page = 10

    relations_to_one = [
        ToOneRelation(
            name='movie_id',
            field_name='movie_id',
            controller=MoviesController,
        ),
        ToOneRelation(
            name='actor_id',
            field_name='actor_id',
            controller=ActorController,
        ),
    ]

    async def photo_field(self, obj):
        actor = await obj.get_relation("actor_id")
        return f'<img ' \
               f'src="https://image.tmdb.org/t/p/w200/' \
               f'{actor.data.url}"' \
               f'width="100">'

    photo_field.is_safe = True

    async def actor_name_field(self, obj):
        actor = await obj.get_relation('actor_id')
        movie = await obj.get_relation('movie_id')
        return actor.data.name + "|" + movie.data.title


@postgres_injector.inject
class GenreMovieController(PostgresController):
    table = movies_genres
    mapper = GenreMoviesMapper
    inline_fields = ['id', 'name', ]

    async def name_field(self, obj) -> str:
        genre = await obj.get_relation('genre_id')
        return genre.data.name

    per_page = 10

    relations_to_one = [
        ToOneRelation(
            name='movie_id',
            field_name='movie_id',
            controller=MoviesController,
        ),
        ToOneRelation(
            name='genre_id',
            field_name='genre_id',
            controller=GenresController,
        ),
    ]
