Contributing
============

You're welcome to come and procrastinate with us :)

Instructions for contribution
-----------------------------

Create your dev database
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ docker-compose up -d
    $ export PGDATABASE=procrastinate PGHOST=localhost PGUSER=postgres
    $ createdb

Installation for development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You may need to install some required packages for psycopg:

.. code-block:: console

    # Ubuntu:
    $ apt install libpq-dev python-dev

If you don't plan to run the code interactively and just want to run tests,
linting and build the doc, you'll just need tox:

.. code-block:: console

    $ pip install tox

If you plan to launch the project locally, install the package itself with development
dependencies:

.. code-block:: console

    $ pip install -r requirements.txt

Testing
^^^^^^^

With a running database:

.. code-block:: console

    (venv) $ pytest  # Test the code with the current interpreter

Or

.. code-block:: console

    $ tox  # Run all the checks for all the interpreters

If you don't know Tox_, have a look at their documentation, it's a very nice tool.

.. _Tox: https://tox.readthedocs.io/en/latest/

Code cleaning
^^^^^^^^^^^^^

Before commiting:

.. code-block:: console

    $ tox -e format

If you've committed already, you can do a "Oops lint" commit, but the best is to run:

.. code-block:: console

    $ git rebase -i --exec 'tox -e format' origin/master

This will run all code formatters on each commits, so that they're clean.
If you've never done an `interactive rebase`_ before, it may seem complicated, so you
don't have to, but... Learn it, it's really cool !

.. _`interactive rebase`: https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History

Try our demo
------------

With a running database:

Launch a worker with:

.. code-block:: console

    (venv) $ export PROCRASTINATE_APP=procrastinate_demo.app.app
    (venv) $ procrastinate migrate
    (venv) $ procrastinate worker

Schedule some tasks with:

.. code-block:: console

    (venv) $ python -m procrastinate_demo
