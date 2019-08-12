=====
Views
=====

List View
---------

By default the list view show only id of instances. For add more fields
for representation you can use *inline_fields* property with list of
fields which you want to show.

.. code-block:: python

    class Books(PostgresView):
        inline_fields = ['username', 'password', ]

Offen we need custom field inside list view. We can do that use
*read_only_fileds* property and representation function for
custom field.

.. code-block:: python

    class Users(PostgresView):
        read_only_fields = ['full_name', ]
        inline_fields = ['id', 'full_name', 'age', ]

        def full_name_field(self, inst):
            return f'{inst.first_name} {inst.last_name}'

The representation function should be named as field which you want to
create with `_field` prefix. Also, in this function you can use
current instance. As result this function must return a string. This
can be simple string or html.

.. note::

    You can sorting your list of instances using all *inline_fields* but
    *read_only_fields* fields are not sorted.

Paggination
-----------

You can customize count of items per page, for that just edit *per_page*
property. By default it set to 50.

.. code-block:: python

    class Books(PostgresView):
        per_page = 20


- list field
- custom field
- pagination
- filters
- sorting
- actions
- bread crumbs
