from markupsafe import Markup
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.controllers.relations import ToManyRelation
from aiohttp_admin2.controllers.relations import ToOneRelation

from ..actors.controllers import ActorController
from ..genres.controllers import GenresController
from ..images.controller import ImageController
from ..injectors import postgres_injector
from ...catalog.tables import movies
from ...catalog.tables import movies_actors
from ...catalog.tables import movies_genres

__all__ = ['MoviesController', 'ActorMovieController', 'GenreMovieController', ]


@postgres_injector.inject
class MoviesController(PostgresController, table=movies):
    name = 'movies'
    per_page = 10
    inline_fields = [
        'poster', 'title', 'status', 'release_date', 'vote_average',
    ]
    search_fields = ['title', ]

    list_filter = ['status', ]
    autocomplete_search_fields = ['title', ]

    async def poster_field(self, obj):
        return Markup(
                '<img'
                '   src="https://image.tmdb.org/t/p/w200/{path}"'
                '   width="100"'
                ' />'
            )\
            .format(path=obj.data.poster_path)

    relations_to_many = [
        ToManyRelation(
            name='Actors',
            left_table_pk='movie_id',
            relation_controller=lambda: ActorMovieController
        ),
        ToManyRelation(
            name='Genres',
            left_table_pk='movie_id',
            relation_controller=lambda: GenreMovieController
        ),
        ToManyRelation(
            name='Images',
            left_table_pk='movie_id',
            relation_controller=ImageController
        ),
    ]

    async def get_object_name(self, obj):
        return f"{obj.get_pk()} - {obj.data.title}"


@postgres_injector.inject
class ActorMovieController(PostgresController, table=movies_actors):
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
        return Markup(
                '<img'
                '   src="https://image.tmdb.org/t/p/w200/{path}"'
                '   width="100"'
                ' />'
            )\
            .format(path=actor.data.url)

    async def actor_name_field(self, obj):
        actor = await obj.get_relation('actor_id')
        movie = await obj.get_relation('movie_id')
        return actor.data.name + "|" + movie.data.title


@postgres_injector.inject
class GenreMovieController(PostgresController, table=movies_genres):
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
