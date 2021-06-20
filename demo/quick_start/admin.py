import typing as t

from aiohttp import web
from aiohttp_admin2.view import DashboardView
from aiohttp_admin2.view.aiohttp.views.template_view import TemplateView
from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.controllers.relations import ToOneRelation
from aiohttp_admin2.controllers.relations import ToManyRelation
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
from aiohttp_admin2 import widgets
from aiohttp_admin2.mappers import fields
from aiohttp_admin2.mappers.validators import length

from .tables import users
from .tables import post
from .tables import postgres_injector


class FirstCustomView(TemplateView):
    name = 'Template view'


class CustomDashboard(DashboardView):
    template_name = 'my_custom_dashboard.html'

    async def get_context(self, req: web.Request) -> t.Dict[str, t.Any]:
        return {
            **await super().get_context(req=req),
            "content": "My custom content"
        }


# create a mapper for table
class UserMapper(PostgresMapperGeneric, table=users):
    pass


# create controller for table with UserMapper
@postgres_injector.inject
class UserController(PostgresController):
    table = users
    mapper = UserMapper
    name = 'user'

    inline_fields = ['id', 'full_name', 'is_superuser', 'joined_at']
    search_fields = ['first_name', 'last_name']
    list_filter = ['joined_at', 'is_superuser', ]

    async def full_name_field(self, obj):
        return f'{obj.data.first_name} {obj.data.last_name}'

    async def get_object_name(self, obj):
        return obj.data.first_name

    relations_to_many = [
        ToManyRelation(
            name='user posts',
            left_table_pk='id',
            right_table_pk='author_id',
            relation_controller=lambda: PostController,
        )
    ]


# create view for table
class UserView(ControllerView):
    controller = UserController


# create a mapper for table
class PostMapper(PostgresMapperGeneric, table=post):
    title = fields.StringField(
        required=True,
        validators=[length(min_value=10)],
    )


# create controller for table with UserMapper
@postgres_injector.inject
class PostController(PostgresController):
    table = post
    mapper = PostMapper
    name = 'post'

    inline_fields = ['id', 'title', 'published_at', 'author_id', ]
    search_fields = ['title', ]
    list_filter = ['status', 'author_id', ]

    async def title_field(self, obj):
        if len(obj.data.title) > 10:
            return f'{obj.data.title[:10]}...'
        return obj.data.title

    relations_to_one = [
        ToOneRelation(
            name='author_id',
            field_name='author_id',
            controller=UserController
        ),
    ]


# create view for table
class PostView(ControllerView):
    controller = PostController

    fields_widgets = {
        'body': widgets.CKEditorWidget
    }
