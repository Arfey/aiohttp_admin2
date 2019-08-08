Templates
=========

For generate pages `aiohttp_admin` using `jinja2`.

If you setup `aiohttp_jinja2` with not default `jinja_app_key`  argument then
you should initialize admin interface with your `jinja_app_key` argument.

.. code-block:: python

    aiohttp_admin.setup(app, jinja_app_key='my_jinja_value')

Overriding templates
--------------------

You can rewrite native templates for `aiohttp_admin`. For that you should
create `admin` directory into templates's directory for the `jinja2`
and create your template with name of template witch you want to rewrite.

The full list of templates you can see below:

- admin/base.html
- admin/create.html
- admin/edit.html
- admin/header.html
- admin/list_action_buttons.html
- admin/list.html
- admin/nav_aside.html
- admin/simple_form.html
- admin/simple_template


Partial customization
---------------------

Very often you need to customization only some template for concretical
model. For that `aiohttp admin` allow you to specify own template for
concretical model.

It's look like this:

.. code-block:: python

    class Books(PostgresView):
        template_edit_name = 'admin/my_edit.html'
