Templates
=========

For generate pages `aiohttp_admin` use `jinja2`.

If you setup `aiohttp_jinja2` with not default `jinja_app_key`  argument then
you should initialize admin interface with your `jinja_app_key` argument.

.. code-block:: python

    aiohttp_admin.setup_admin(app, jinja_app_key='my_jinja_value')

Overriding templates
--------------------

You can rewrite native templates for `aiohttp_admin`. For that you should
create `aiohttp_admin` directory into templates's directory for the `jinja2`
and create your template with name of template witch you want to rewrite.

The full list of templates you can see below:

- admin/index.html
