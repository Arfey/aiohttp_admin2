Usage
=====


Authorization & Permissions
---------------------------

Authorization
.............

If you need an authorization to the your admin interface then you can add
custom middleware to achieve this goal. It might look like this:

.. code-block:: python

    from aiohttp import web
    from aiohttp_security import is_anonymous
    from aiohttp_security import permits
    from aiohttp_admin2 import setup_admin


    @web.middleware
    async def admin_access_middleware(request, handler):
        if await is_anonymous(request):
            raise web.HTTPFound('/')

        if not await permits(request, 'admin'):
            raise web.HTTPFound('/')

        return await handler(request)


    setup_admin(
        application,
        # You can specify here a list of middlewares which you want to apply
        # to each request related with admin interface
        middleware_list=[admin_access_middleware, ],
        ...
    )


In the snippet above we just check that user is not anonymous and has admin
permissions. The logic of `is_anonymous` and `permits` you have to implement
by yourself because admin just guarantee the for each admin route will apply
list of middlewares which you specify in the **middleware_list** param.

The `aiohhtp_admin2` don't provide any views for login/logout logic so all of
this logic you need implement by yourself.

Permissions
...........

For organization permissions in your admin interface you have to use the
`access_hook` method in the view class. Since the `aiohhtp_admin2` instantiate
new view for each request and after that run `access_hook` method therefore
inside this method you can easy change any propery of the current view instance
to restrict access.

As an example you have a ActorView class and you want to show information
related with this view only for users who have correct rights for that.


.. code-block:: python

    from aiohttp_admin2.view import ControllerView


    class ActorView(ControllerView):
        controller = ActorController

        async def access_hook(self) -> None:
            if not user_can_view(self.request, 'aсtors'):
                self.has_access = False

In `access_hook` method we can to get current request so we just pass it to the
predicate function (`user_can_view`) and change property if need. If user
without right access visit any route related with current view then he gets
the `PermissionDenied` exception. If you want only hide view from aside menu
than you have to use `is_hide_view` property instead.

Let's consider case when you need to give only read right or give right to
create but without edit rights.


.. code-block:: python

    from aiohttp_admin2.view import ControllerView


    class ActorView(ControllerView):
        controller = ActorController

        async def access_hook(self) -> None:
            # here we get controller instance of the current view
            controller = self.get_controller()

            controller.can_view = user_can_view(self.request, 'aсtors')
            controller.can_edit = user_can_edit(self.request, 'aсtors')
            controller.can_delete = user_can_delete(self.request, 'aсtors')
            controller.can_create = user_can_create(self.request, 'aсtors')

            if is_guest(self.request):
              controller.inline_fields = ['id', ]
              self.template_detail_name = 'aiohttp_admin/detail_view_for_guest.html'
              controller.per_page = 20

We can change any property of controller even `inline_fields` or `per_page`
if we need to do that.

.. warning::
    The `access_hook` method is async function so you actually can to do
    request to databases inside it to check permission but it's not a good
    idea because for each request the admin call this method for each view
    (to check that we can show link to views in aside menu) and that can
    produce n + 1 requests. The better approach is get all rights inside
    `middelware` and set this info to request and inside `access_hook` method
    just check that request contain right access.


Mappers
-------

Mapper need for describe data which use for create or update instances. You can create mapper in two ways.

Custom mappers
..............

You can create your own mapper with custom fields:

.. code-block:: python

    from aiohttp_admin2.mappers import Mapper
    from aiohttp_admin2.mappers import fields


    class UserMapper(Mapper):
        """Mapper for user instance."""
        name = fields.StringField(required=True)
        age =  field.IntField(default=18)

Mappers generator
.................

If you create admin page for SQLalchemy or Umongo instances then you can
generate mapping automatically by specifying models.

.. code-block:: python

    from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
    from aiohttp_admin2.mappers import fields


    user = sa.Table('user', metadata,
        sa.Column('name', sa.String(255)),
        sa.Column('age', sa.Integer),
    )


    class UserMapper(PostgresMapperGeneric, table=user):
        """Mapper for user instance."""
        pass

but if you want to rewrite some field you can do it some like that

.. code-block:: python

    from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
    from aiohttp_admin2.mappers import fields


    class UserMapper(PostgresMapperGeneric, table=user):
        """Mapper for user instance."""
        age = fields.StringField(required=True)

In this case generic will generate all fields for you but will use age field
which you specify.

# todo: validation

Fields
......

**StringField** - field for represented string data.

- *required* - add validation for empty value if set to `True`
- *default* - replace empty value if specify
- *validators* - list of validators

**IntField** - field for represented integer data.

- *required* - add validation for empty value if set to `True`
- *default* - replace empty value if specify
- *validators* - list of validators

**FloatField** - field for represented float data.

- *required* - add validation for empty value if set to `True`
- *default* - replace empty value if specify
- *validators* - list of validators

**DateTimeField** - field for represented datetime data.

- *required* - add validation for empty value if set to `True`
- *default* - replace empty value if specify
- *validators* - list of validators

**BooleanField** - field for represented boolean data. If value contains '0',
'false' or 'f' than value will be parse as `False` in other case as `True`.

- *required* - add validation for empty value if set to `True`
- *default* - replace empty value if specify
- *validators* - list of validators

**ChoicesField** - add predefined values. If you have some finite list of values
and want that this list will represented like select tag you need to use
current field type.

- *required* - add validation for empty value if set to `True`
- *default* - replace empty value if specify
- *validators* - list of validators
- *field_cls* - field type which will represent selected value
- *choices* - tuple of tuple with values.

.. code-block:: python

    from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
    from aiohttp_admin2.mappers import fields


    class UserMapper(PostgresMapperGeneric, table=user):
        """Mapper for user instance."""
        GENDER_CHOICES = (
            ('male', "male"),
            ('female', "female"),
        )

        gender = fields.ChoicesField(
            field_cls=fields.StringField,
            choices=GENDER_CHOICES,
            default='male'
        )

Controllers
-----------

The controller is class that generate access to the your data based on some
engine. Out of the box you have engines for different storages

- PostgreSQL
- MySQL
- MongoDB

but you actually can easy to add your own engine (Resource).

The controller is framework and database agnostic part of the admin. It's mean
that controller have not to know any about request/response, generation of
urls, templates and so on. Also it have not to know about how to
get/update/delete date from some database (this logic need to allocate
into the resource class).

For the PostgreSQL, an easier way to create a controller is to use the
`PostgresController`.


.. code-block:: python

    from aiohttp_admin2.controllers.postgres_controller import PostgresController


    @postgres_injector.inject
    class UserController(PostgresController):
        table = user
        mapper = UserMapper
        name = 'user'
        per_page = 10

- read_only_fields - list of fields which can't modify
- inline_fields - list of fields which will show on list page
- can_create - True if can to edit instance
- can_update - True if can to update instance
- can_delete - True if can to delete instance
- can_view - True if can to show instance
- order_by - field for order ('-id', 'id')
- per_page - number of item per page


The Controller need to have connection for engine. For this goal we need to
inject connection by `ConnectionInjector`.

.. code-block:: python

    from aiohttp_admin2.connection_injectors import ConnectionInjector


    postgres_injector = ConnectionInjector()


    async def init_db(app):
        # Context function for initialize connection to db
        engine = await aiopg.sa.create_engine(
            user='postgres',
            database='postgres',
            host='0.0.0.0',
            password='postgres',
        )
        app['db'] = engine

        # here we add connection for our injector
        postgres_injector.init(engine)

After that you can user `postgres_injector` to decorate your controllers. For
`MongoController` you don't need to use `ConnectionInjector` because connection
to db exist in table instance.

Access
......

Admin interface have two approaches for restrict access:

- global middleware
- `access_hook` for each controller

Global middleware use for restrict access to whole admin interface. It might
look something like this:

.. code-block:: python

    from aiohttp import web


    @web.middleware
    async def admin_access_middleware(request, handler):
        """
        This middleware need for forbidden access to admin interface for users
        who don't have right permissions.
        """
        if await is_anonymous(request):
            raise web.HTTPFound('/')

        if not await permits(request, 'admin'):
            raise web.HTTPFound('/')

        return await handler(request)

This middleware you can apply for admin interface using `middleware_list`
parameter.

.. code-block:: python

    setup_admin(
        application,
        # ...
        middleware_list=[admin_access_middleware, ],
        logout_path='/logout',
    )

also you can specify `logout_path` parameter to add logout button inside admin
header navigation bar.




If you need to make access to some instances you cat do it using: can_create,
can_update, can_view, can_delete.
If access must be specify by some user you also cat use `access_hook`.
`access_hook` - access hook use before for each access to data.

.. code-block:: python

    class UserController(PostgresController):
        ...

        async def access_hook(self):
            if some_expression():
                self.can_create = False
                self.can_update = False

Operations hooks
................

If you need to do some before/after create/update or delete some data you can
use hooks:

- pre_create - run before create instance
- pre_delete - run before delete instance
- pre_update - run before update instance
- post_create - run after create instance
- post_delete - run after delete instance
- post_update - run after update instance

# todo: example

Views
-----

This class use for represent data on admin interface.

ControllerView
..............

.. code-block:: python

    from aiohttp_admin2.view import ControllerView


    class UserPage(ControllerView):
        controller = UserController


- is_hide_view - if False page will not to show in admin interface
- title - title for page
- group_name - name of group


TemplateView
............

.. code-block:: python

    from aiohttp_admin2.view import TemplateView


    class NewPage(TemplateView):
        title = 'new page'

- template_name - path to template for current page


Templates
---------

For generate pages `aiohttp_admin` use `jinja2`.

If you setup `aiohttp_jinja2` with not default `jinja_app_key`  argument then
you should initialize admin interface with your `jinja_app_key` argument.

.. code-block:: python

    aiohttp_admin.setup_admin(app, jinja_app_key='my_jinja_value')

Overriding jinja templates
..........................

You can rewrite native templates for `aiohttp_admin`. For that you should
create `aiohttp_admin` directory into templates's directory for the `jinja2`
and create your template with name of template witch you want to rewrite.

The full list of templates you can see below:

- aiohttp_admin/base.html - base layout
- aiohttp_admin/create.html - content for create page
- aiohttp_admin/delete.html - content for confirm delete page
- aiohttp_admin/detail.html - content for view detail page
- aiohttp_admin/detail_edit.html - content for edit page
- aiohttp_admin/form.html - main form for create and update
- aiohttp_admin/header.html - header for base layout
- aiohttp_admin/list.html - content for list page
- aiohttp_admin/list_action_buttons.html - list actions for list page
- aiohttp_admin/nav_aside.html - aside with pages
- aiohttp_admin/pagination.html - pagination block
- aiohttp_admin/template_view.html - content template for custom page


Overriding view templates
.........................

You also can specify template for some special `ControllerView`.


.. code-block:: python

    class UserPage(ControllerView):
        controller = UserController

        template_list_name = 'aiohttp_admin/list.html'
        template_detail_name = 'aiohttp_admin/detail.html'
        template_detail_edit_name = 'aiohttp_admin/detail_edit.html'
        template_detail_create_name = 'aiohttp_admin/create.html'
        template_delete_name = 'aiohttp_admin/delete.html'


Resources
---------
