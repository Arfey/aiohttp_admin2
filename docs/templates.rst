Templates
=========

For generate pages `aiohttp_admin` using `jinja2`. You can rewrite native
templates for `aiohttp_admin`. For that you should create `admin` directory
into templates's directory for the `jinja2` and create your template with name
of template witch you want to rewrite.

If you setup `aiohttp_jinja2` with not default `jinja_app_key`  argument then
you should initialize admin interface with your `jinja_app_key` argument.

.. code-block:: python

    aiohttp_admin.setup(app, jinja_app_key='my_jinja_value')
