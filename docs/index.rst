Aiohttp admin documentation
===========================

`Demo site
<https://shrouded-stream-28595.herokuapp.com/>`_ | `Demo source code
<https://github.com/Arfey/aiohttp_admin2/tree/master/aiohttp_admin2/demo/>`_.

.. image:: https://img.shields.io/pypi/v/aiohttp_admin2.svg
        :target: https://pypi.python.org/pypi/aiohttp_admin2

.. image:: https://img.shields.io/travis/arfey/aiohttp_admin2.svg
        :target: https://travis-ci.com/arfey/aiohttp_admin2

.. image:: https://readthedocs.org/projects/aiohttp-admin2/badge/?version=latest
        :target: https://aiohttp-admin2.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/arfey/aiohttp_admin2/shield.svg
     :target: https://pyup.io/repos/github/arfey/aiohttp_admin2/
     :alt: Updates

The aiohttp admin is a library for build admin interface for applications based
on the aiohttp. With this library you can ease to generate CRUD views for your
data (for data storages which support by aiohttp admin) and flexibly customize
representation and access to these.

.. image:: /images/index.png

Installation
------------

The first step which you need to do it’s installing library

.. code-block:: bash

   pip install aiohttp_admin2

If you need more detail information about installation look at :ref:`installation` section.

Quick start
-----------

For simple start you need just import setup admin function and extend your
existing aiohttp application. For example:

`admin.py`

.. code-block:: python

    from aiohttp import web
    from aiohttp_admin2 import setup_admin

    app = web.Application()

    # setup admin interface
    setup_admin(app)

    web.run_app(app)

And run `python admin.py`. That is it. Now you can open in your browser
*http://localhost:8080/admin/* and see home page of the our awesome admin
interface.

.. image:: /images/simple_example.png

**Dashboard**

.........

The first page which you see when setup admin is dashboard. This is startup
page and you can to customize it. For that u need to create your custom
dashboard's class

.. code-block:: python

    from aiohttp import web
    from aiohttp_admin2.views import DashboardView


    class CustomDashboard(DashboardView):
        async def get_context(self, req: web.Request):
            return {
                **await super().get_context(req=req),
                "content": "My custom content"
            }

You can rewrite get_context method and put your new content to the jinja
context. After that we need to create your custom admin class and put it into
setup function:

.. code-block:: python

    from aiohttp import web
    from aiohttp_admin2 import setup_admin
    from aiohttp_admin2.views import Admin


    class CustomAdmin(Admin):
        dashboard_class = CustomDashboard

    app = web.Application()

    # setup admin interface
    setup_admin(app, admin_class=CustomAdmin)

    web.run_app(app)

.. image:: /images/custom_context.png

As the alternative way we can to redefine the template for the our dashboard.
The first thing which we need to do is create a new dashboard template.


`templates/my_custom_dashboard.html`

.. code-block:: html

    {% extends 'aiohttp_admin/layouts/base.html' %}

    {% block main %}
      <h1>Dashboard</h1>
      <b>{{ content }}...</b>
    {% endblock main %}

we nested from the base html template and put to the main block our new
content. The second step is declare this template in the `CustomDashboard`.

.. code-block:: python

    class CustomDashboard(DashboardView):
        # redefine `template_name` attribute to your own
        template_name = 'my_custom_dashboard.html'
        ...

The last step is setup jinja for your application and set path to the your
templates directory

.. code-block:: python

    import aiohttp_jinja2
    import jinja2
    from pathlib import Path

    # path to the your template directory
    templates_directory = Path(__file__).parent / 'templates'

    app = web.Application()

    # setup jinja2
    aiohttp_jinja2.setup(
        app=application,
        loader=jinja2.FileSystemLoader(str(templates_directory)),
    )

    # setup admin interface
    setup_admin(app, admin_class=CustomAdmin)

    web.run_app(app)

As result you can see that dashboard use your custom html.

.. image:: /images/custom_template_name_dashboard.png


**Custom views**

.........

The next thing which you can to do with your admin interface is create your own
custom view. For that you need just create a new view and setup it together
with admin interface. After that you can to see a new tab in the aside bar.

.. code-block:: python

    from aiohttp_admin2.views.aiohttp.views.template_view import TemplateView


    class FirstCustomView(TemplateView):
        name = 'Template view'


    # setup admin interface
    setup_admin(
        application,
        admin_class=CustomAdmin,
        # put here your new template view to register it
        views=[FirstCustomView,]
    )


The DashboardView class nested from the TemplateView class so you can do with
it all things which we considered above for DashboardView class (redefine
context and template).

.. image:: /images/template_page.png

If you don't want add current web page to the aside bar then you can specify
`is_hide_view` attribute to `True`.

.. code-block:: python

    class FirstCustomView(TemplateView):
        name = 'Template view'
        # remove link from aside bar
        is_hide_view = True

In this case you can to visit this web page got to the directly via url but
admin interface will not to show any links to it.

**CRUD views**

.........

The most helpful thing in the aiohttp_admin2 is possible to generate views
based on models on your data from different databases.

Right now the library support models for:

- SQLAlchemy (postgres/mysql)
- umongo (mongodb)

So, if you have a above models then you can easy add create/delete/update views
in the your admin interface. Let's consider a simple example how it might looks
like for the SQLAlchemy.


Let's assume we have current SQLAlchemy's models:


.. code-block:: python

    from enum import Enum

    import sqlalchemy as sa


    metadata = sa.MetaData()


    class PostStatusEnum(Enum):
        published = 'published'
        not_published = 'not published'


    users = sa.Table('users', metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('first_name', sa.String(255)),
        sa.Column('last_name', sa.String(255)),
        sa.Column('is_superuser', sa.Boolean),
        sa.Column('joined_at', sa.DateTime()),
    )

    books = sa.Table('post', metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(255)),
        sa.Column('body', sa.Text),
        sa.Column('status', sa.Enum(PostStatusEnum)),
        sa.Column('published_at', sa.DateTime()),
        sa.Column('author_id', sa.ForeignKey('users.id', ondelete='CASCADE')),
    )

We have the simple users table and the posts table where allocated posts which
have been created via our users. Users and posts tables related by foreignKey
`author_id`.

The first thing which we need to do before start to generate CRUD views is set
up the PostgreSQL connection in the our application


.. code-block:: python

    import aiopg.sa
    from aiohttp_admin2.connection_injectors import ConnectionInjector


    postgres_injector = ConnectionInjector()


    async def init_db(app):
        engine = await aiopg.sa.create_engine(
            user='postgres',
            database='postgres',
            host='0.0.0.0',
            password='postgres',
        )
        app['db'] = engine

        # set our engine to the postgres_injector
        postgres_injector.init(engine)

        yield

        app['db'].close()
        await app['db'].wait_closed()

    application = web.Application()
    application.cleanup_ctx.extend([init_db])


It's a standard way to set up connection to the database into aiohttp but we
have new lines related with `ConnectionInjector`. `ConnectionInjector` is just
a class which used to share database connection with between aiohttp and admin
library.

The second thing is create registered our model for the admin.

.. code-block:: python

    from aiohttp_admin2.views import ControllerView
    from aiohttp_admin2.controllers.postgres_controller import PostgresController
    from aiohttp_admin2.mappers.generics import PostgresMapperGeneric


    # create a mapper for table
    class UserMapper(PostgresMapperGeneric, table=users):
        pass


    # create controller for table with UserMapper
    @postgres_injector.inject
    class UserController(PostgresController):
        table = users
        mapper = UserMapper
        name = 'user'


    # create view for table
    class UserView(ControllerView):
        controller = UserController

And after that setup our admin interface with the `UserView`.


.. code-block:: python

    # setup admin interface
    setup_admin(
        application,
        admin_class=CustomAdmin,
        views=[
            FirstCustomView,
            UserView, # added new view
        ]
    )

Now, you can to see that admin interface has new tab in the aside bar and we
have simple list, create, update and delete pages for the our user model.

`List page`

.. image:: /images/simple_list.png

`Create page`

.. image:: /images/simple_create.png

`Update page`

.. image:: /images/simple_update.png

`Delete page`

.. image:: /images/simple_delete.png


Let's make our list page view a little bit better. For that we can to show to
user more information using `inline_fields` attribute in the `UserController`
class.

.. code-block:: python

    @postgres_injector.inject
    class UserController(PostgresController):
        table = users
        mapper = UserMapper
        name = 'user'

        inline_fields = ['id', 'full_name', 'is_superuser', 'joined_at']


Our table has `id`, `is_superuser` and `joined_at` but don't has `full_name`
but for end user we want to show full name. For do that we can to use custom
filed and add to our class the `full_name_field` method (<field_name>_field).


.. code-block:: python

    @postgres_injector.inject
    class UserController(PostgresController):

        ...

        async def full_name_field(self, obj):
            return f'{obj.data.first_name} {obj.data.last_name}'


Also we want to give a possible to user use search by `fist_name` and
`last_name` fields. We can easy do that by add `search_fields` attribute and
specify list of fields which we want to use to search.


.. code-block:: python

    @postgres_injector.inject
    class UserController(PostgresController):

        ...

        search_fields = ['first_name', 'last_name']


And as final step we want to give a possible to filter a list of our data. For
achieve this goal we need only specify list of fields which will use for
filtering to the `list_filter` attribute.


.. code-block:: python

    @postgres_injector.inject
    class UserController(PostgresController):

        ...

        list_filter = ['joined_at', 'is_superuser', ]

After that view of our list page become much better

.. image:: /images/full_controller_example.png

Let's make the same for the post model

.. code-block:: python

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


    # create view for table
    class PostView(ControllerView):
        controller = PostController

The post table has `title` field but we want to change view of this field. In
this cases we can also to use the custom field (`title_field`).

.. image:: /images/post_controller_first.png

Okay. We has a representation of the post and the user models. This models have
relations between each other and we need to show it in the admin interface.

First relation is one to one relation between post and author. Single post has
only one author. To show this relation we can to specify `relations_to_one`
attribute.


.. code-block:: python

    from aiohttp_admin2.controllers.relations import ToOneRelation


    @postgres_injector.inject
    class PostController(PostgresController):

        ...

        relations_to_one = [
            ToOneRelation(
                # the field name of current relation
                name='author_id',
                # the name of field which responsible for relation (foreignkey)
                field_name='author_id',
                # controller of the relation model
                controller=UserController
            ),
        ]


    @postgres_injector.inject
    class UserController(PostgresController):

        ...

        async def get_object_name(self, obj):
            # need just for better representation instances of current model
            return obj.data.first_name

In `ToOneRelation` we put `name` of field which will represented current
relation (in our case we replace existing `author_id` field) and `field_name`
field in table which responsible for current relation and controller of the
relation model. After that we has link to the relational model on list page and
autocomplete on create/update page.


.. image:: /images/one_to_one_relation_list.png
.. image:: /images/one_to_one_relation_autocomplete.png


The second relation is one to many relation between auth and posts. User
can has many posts. To show this relation we can to specify `relations_to_many`
attribute.

.. code-block:: python

    from aiohttp_admin2.controllers.relations import ToManyRelation

    @postgres_injector.inject
    class UserController(PostgresController):

        ...

        relations_to_many = [
            ToManyRelation(
                # the name of current relation
                name='user posts',
                # the name of field which responsible for relation in the
                # current table
                left_table_pk='id',
                # the name of field which responsible for relation in the
                # other table
                right_table_pk='author_id',
                # controller of the relation model (we can use controller
                # class or callable function which return it).
                relation_controller=lambda: PostController,
            )
        ]


In `ToManyRelation` we put `name` which will use as title of the current
relation, left_table_pk and right_table_pk which describe fields which
responsible for relation between tables and `relation_controller` which
receive the controller class of related model. After that we'll have a tab bar
on detail page of author model. On this tab we see all post of the current
user.


.. image:: /images/one_to_one_example.png

We are continuing improve admin interface and next step is customize detail
page of the post model. The first thing which we can to improve its add html
editor for the body field. Widgets responsible for view of input on detail
page and we can change these for some particular type of field or for
concretical field.


.. code-block:: python

    from aiohttp_admin2.views import widgets


    # create view for table
    class PostView(ControllerView):
        controller = PostController

        fields_widgets = {'body': widgets.CKEditorWidget}

Two lines of code and we have a html editor for body field.

.. image:: /images/body_field_html.png

Also let's assume that we need to add some validation on create/update post in
the admin interface. We can to do that via mappings. Mapping responsible for
validation of data in aiohttp admin.

.. code-block:: python

    class PostMapper(PostgresMapperGeneric, table=post):
        title = fields.StringField(
            required=True,
            validators=[length(min_value=10)],
        )

The `PostgresMapperGeneric` mapper generate all fields of table but if we need
specify for these fields some properties we need to redefine these. We just
redefined title field to make it required and add validator to avoide cases
when title will less then 10 symbol. Now, if we try to create a post with small
title that we'll see an error message.

.. image:: /images/validation_error_example.png

The source code of current examples you might to find `here
<https://github.com/Arfey/aiohttp_admin2/tree/master/demo/quick_start/>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   controllers
   mappers
   views
   resources
   templates
   modules
   contributing
   authors
   history

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
