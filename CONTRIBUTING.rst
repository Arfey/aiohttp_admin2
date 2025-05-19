.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/arfey/aiohttp_admin2/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

aiohttp admin 2 could always use more documentation, whether as part of the
official aiohttp admin 2 docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/arfey/aiohttp_admin2/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `aiohttp_admin2` for local development.

1. Fork the `aiohttp_admin2` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/aiohttp_admin2.git

3. You need to have preinstalled poetry and docker.

    $ poetry config virtualenvs.create true --local # create virtualenv in project directory
    $ cd aiohttp_admin2/
    $ poetry install --with "dev, test" --all-extras

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. Install dependencies

    $ pip install pre-commit
    $ poetry install --with "dev, test" --all-extras

6. When you're done making changes, check that your changes pass linters and
   tests::

    $ make lint
    $ make test

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website.

Tips
----

To run a subset of tests::


    $ pytest --slow -v -s -p no:warnings  tests/resources/common_resource


Run some particular test::


    $ pytest --slow -v -s -p no:warnings  tests/resources/common_resource/test_create.py::test_create_with_error


All features you can to test in demo application.
