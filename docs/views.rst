=====
Views
=====

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
