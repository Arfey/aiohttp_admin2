Tutorial
========

In this tutorial we step by step learn how to create a greate admin
interface with `aiohttp_admin`.

=======================
1 - step: Setup aiohttp
=======================

The first think that we need it's create a test project.

.. code-block:: console

    mkdir my_project
    cd my project
    touch __init__.py

After that, we need to have aiohttp

.. code-block:: console

    pip install aiohttp

Write a simple aiohttp application as in example bellow


`__init__.py`

.. code-block:: python

    from aiohttp import web

    async def hello(request):
        return web.Response(text="Hello, world")

    app = web.Application()
    app.add_routes([web.get('/', hello)])
    web.run_app(app)

And after that you can run your application and open browser localhost:8080


.. code-block:: console

    python3 __init__.py

If you saw `Hello, world` it's grate and we can go to the next step.


=============================
2 - step: Setup aiohttp_admin
=============================

For setup `aiohttp_admin` you need just wrap your application use setup
function.


`__init__.py`

.. code-block:: python

    from aiohttp import web
    from aiohttp_admin.setup import setup

    async def hello(request):
        return web.Response(text="Hello, world")

    app = web.Application()
    app.add_routes([web.get('/', hello)])
    setup(app)
    web.run_app(app)
