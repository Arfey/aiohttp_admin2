Aiohttp admin documentation
===========================

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

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   installation
   usage
   modules
   templates
   contributing
   authors
   history

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
