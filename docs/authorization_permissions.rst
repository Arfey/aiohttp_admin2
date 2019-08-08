Authorization & Permissions
=========================

The `aiohttp admin` provide the approach for forbidden some of
*create / update / delete action* in some cases. For that we have
*access_hook*.


.. code-block:: python

    class Book(PostgresView):
        def access_hook(self, req):
            if not is_admin(req):
                self.can_update = True
                self.can_delete = True


In the example above **is_admin** is't your function that check
if the user administrator or not.  If it's not administrator
than we forbidden edit and delete data. For that we use some properties:


- *can_create* - access to create a new instance
- *can_update* - access to update an existing instance
- *can_view_list* - access to view list of instances
- *can_delete* - access to remove an instance

The **access_hook** run before run handler of request so in this method
you can change view for some user. As example you can change *read_only_fields*.

.. code-block:: python

    class Book(PostgresView):
        read_only_fields = ['title', 'description', 'const']

        def access_hook(self, req):
            if not is_admin(req):
                self.read_only_fields = ['title', 'description']

In this case only an administrator have access to change cost of a book.
Or in the most simple way just return forbidden status.

.. code-block:: python

    class Book(PostgresView):
        def access_hook(self, req):
            if not is_admin(req):
                raise web.HTTPForbidden()
