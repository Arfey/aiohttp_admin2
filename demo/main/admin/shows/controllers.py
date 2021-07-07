from markupsafe import Markup
from aiohttp_admin2.views import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.controllers.relations import ToManyRelation
from aiohttp_admin2.controllers.relations import ToOneRelation

from ...catalog.tables import shows
from ...catalog.tables import shows_actors
from ...catalog.tables import shows_genres
from ...catalog.tables import shows_seasons
from ..actors.controllers import ActorController
from ..genres.controllers import GenresController
from ..images.controller import ImageController
from ..injectors import postgres_injector


@postgres_injector.inject
class ShowsController(PostgresController, table=shows):
    name = 'shows'
    per_page = 10

    search_fields = ['title', ]
    inline_fields = [
        'poster', 'title', 'status', 'first_air_date', 'last_air_date',
        'vote_average',
    ]

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
            relation_controller=lambda: ActorShowController
        ),
        ToManyRelation(
            name='Genres',
            left_table_pk='show_id',
            relation_controller=lambda: GenreShowController
        ),
        ToManyRelation(
            name='Seasons',
            left_table_pk='show_id',
            relation_controller=lambda: SeasonShowController
        ),
        ToManyRelation(
            name='Images',
            left_table_pk='show_id',
            relation_controller=ImageController
        ),
    ]


@postgres_injector.inject
class ActorShowController(PostgresController, table=shows_actors):
    inline_fields = [
        'id', 'poster', 'actor_id', 'actor', 'character', 'order'
    ]
    order_by = 'order'
    list_filter = ['id']

    per_page = 10

    relations_to_one = [
        ToOneRelation(
            name='movie_id',
            field_name='movie_id',
            controller=ShowsController,
        ),
        ToOneRelation(
            name='actor_id',
            field_name='actor_id',
            controller=ActorController,
        ),
    ]

    async def actor_field(self, obj):
        actor = await obj.get_relation('actor_id')
        return actor.data.name

    async def poster_field(self, obj):
        actor = await obj.get_relation("actor_id")

        return Markup(
                '<img'
                '   src="https://image.tmdb.org/t/p/w200/{path}"'
                '   width="100"'
                ' />'
            )\
            .format(path=actor.data.url)


@postgres_injector.inject
class GenreShowController(PostgresController, table=shows_genres):
    inline_fields = ['id', 'name', ]

    per_page = 10

    relations_to_one = [
        ToOneRelation(
            name='show_id',
            field_name='show_id',
            controller=ShowsController
        ),
        ToOneRelation(
            name='genre_id',
            field_name='genre_id',
            controller=GenresController
        )
    ]

    async def name_field(self, obj) -> str:
        genre = await obj.get_relation('genre_id')
        return genre.data.name


@postgres_injector.inject
class SeasonShowController(PostgresController, table=shows_seasons):
    inline_fields = ['poster', 'season_number', 'episode_count', 'air_date', ]

    per_page = 10

    relations_to_one = [
        ToOneRelation(
            name='show_id',
            field_name='show_id',
            controller=ShowsController
        )
    ]

    async def genre_name_field(self, obj) -> str:
        genre = await obj.get_relation('genre_id')
        return genre.data.name

    async def poster_field(self, obj):
        return Markup(
                '<img'
                '   src="https://image.tmdb.org/t/p/w200/{path}"'
                '   width="100"'
                ' />'
            )\
            .format(path=obj.data.poster_path)


class ShowsPage(ControllerView):
    controller = ShowsController
