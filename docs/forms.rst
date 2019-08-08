Forms
=====

The *aiohttp admin's* form need for validate data. The form have fields
that need to represent data and fields have a widget that provide a
view of field and field's data.


Workflow with Form
------------------

The form can generate fields from the some SQLAlchemy's table.

.. code-block:: python

    import sqlalchemy as sa
    from aiohttp_admin.core.generate import PostgresAdminForm

    # table
    metadata = sa.MetaData()
    users_table = sa.Table('users', metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.Text),
        sa.Column('password', sa.Text),
    )

    # generated form
    class UserForm(PostgresAdminForm, table=users_table):
        pass

In this case *aiohttp admin* generate fields instead of you. If you want to
specify field by himself you can override it.

.. code-block:: python

    from aiohttp_admin.core import fields

    class UserForm(PostgresAdminForm, table=users_table):
        username = fields.TextField(required=True)
