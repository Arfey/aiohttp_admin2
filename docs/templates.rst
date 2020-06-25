Templates
=========

For generate pages `aiohttp_admin` use `jinja2`.

If you setup `aiohttp_jinja2` with not default `jinja_app_key`  argument then
you should initialize admin interface with your `jinja_app_key` argument.

.. code-block:: python

    aiohttp_admin.setup_admin(app, jinja_app_key='my_jinja_value')

Overriding jinja templates
--------------------------

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
-------------------------

You also can specify template for some special `ControllerView`.


.. code-block:: python

    class UserPage(ControllerView):
        controller = UserController

        template_list_name = 'aiohttp_admin/list.html'
        template_detail_name = 'aiohttp_admin/detail.html'
        template_detail_edit_name = 'aiohttp_admin/detail_edit.html'
        template_detail_create_name = 'aiohttp_admin/create.html'
        template_delete_name = 'aiohttp_admin/delete.html'
