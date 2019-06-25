.. include:: ../README.rst

Installation
============

.. code-block:: bash

   pip install aiohttp_admin

Quick start
===========

.. code-block:: python

    from aiohttp import web
    from aiohttp_admin.setup import setup

    def create_app():
        app = web.Application()
        setup(app)

        return app

and after open *http://localhost:8080/admin/* in your browser.

.. image:: /image/simple_example.png

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   tutorial
   views
   models
   templates
   authorization_permissions
   q&a
   modules
   contributing
   history

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
