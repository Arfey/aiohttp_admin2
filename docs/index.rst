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

The aiohttp admin is library for generate admin interface for your data based
on aiohttp. This interface support multiple data storages and can combine them
together.

Installation
============

The first step which you need to do it’s installing library

.. code-block:: bash

   pip install aiohttp_admin2

If you need more detail information about installation look at :ref:`installation` section.

Quick start
===========

For simple start you need just import setup admin function and extend your
existing aiohttp application.

.. code-block:: python

    from aiohttp import web
    from aiohttp_admin2 import setup_admin

    app = web.Application()
    setup_admin(app)

    web.run_app(app)

That is it. Now you can open in your browser *http://localhost:8080/admin/* and
see home page of our awesome admin interface.

.. image:: /images/simple_example.png

If you use sqlalchemy then simple example with integration can be looks like this.

.. code-block:: python

    from aiohttp import web
    from aiohttp_admin2 import setup_admin
    from aiohttp_admin2.view import ControllerView
    from aiohttp_admin2.controllers.postgres_controller import PostgresController
    from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
    from aiohttp_admin2.connection_injectors import ConnectionInjector
    import sqlalchemy as sa


    # describe a table
    metadata = sa.MetaData()
    postgres_injector = ConnectionInjector()

    tbl = sa.Table('tbl', metadata,
       sa.Column('id', sa.Integer, primary_key=True),
       sa.Column('val', sa.String(255)),
    )

    # create a mapper for table
    class UserMapper(PostgresMapperGeneric, table=tbl):
        pass

    # create controller for table with UserMapper
    @postgres_injector.inject
    class UserController(PostgresController):
        table = tbl
        mapper = UserMapper
        name = 'user'

    # create view for table
    class UserPage(ControllerView):
        controller = UserController


    app = web.Application()

    engine = await create_engine(user='postgres',
                                 database='postgres',
                                 host='0.0.0.0',
                                 password='postgres').__aenter__()
    postgres_injector.init(engine)

    setup_admin(
        app,
        # put our views
        views=[UserPage, ],
    )

    web.run_app(app)


.. image:: /images/simple_list_example.png

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
