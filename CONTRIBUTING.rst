Contributing
============

You're welcome to come and procrastinate with us :)

Instructions for contribution
-----------------------------

Create your development database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ sudo apt install postgresql-client
    $ docker-compose up -d
    $ export PGDATABASE=procrastinate PGHOST=localhost PGUSER=postgres
    $ createdb

Set up your development environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You may need to install some required packages for ``psycopg2``:

.. code-block:: console

    # Ubuntu:
    $ apt install libpq-dev python-dev

If you don't plan to run the code interactively and just want to run tests,
linting and build the doc, you'll just need ``tox``:

.. code-block:: console

    $ pip install tox

If you plan to launch the project locally, install the package itself with development
dependencies in a virtual environment:

.. code-block:: console

    $ python3 -m venv .venv
    $ source .venv/bin/activate
    (venv) $ pip install -r requirements.txt

Run the project automated tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With a running database:

.. code-block:: console

    (venv) $ pytest  # Test the code with the current interpreter

Or

.. code-block:: console

    $ tox  # Run all the checks for all the interpreters

If you don't know Tox_, have a look at their documentation, it's a very nice tool.

.. _Tox: https://tox.readthedocs.io/en/latest/

To look at coverage in the browser after launching the tests, use:

.. code-block:: console

    $ python -m webbrowser htmlcov/index.html

Keep your code clean
^^^^^^^^^^^^^^^^^^^^

Before committing:

.. code-block:: console

    $ tox -e format

If you've committed already, you can do a "Oops lint" commit, but the best is to run:

.. code-block:: console

    $ git rebase -i --exec 'tox -e format' origin/master

This will run all code formatters on each commits, so that they're clean.
If you've never done an `interactive rebase`_ before, it may seem complicated, so you
don't have to, but... Learn it, it's really cool !

.. _`interactive rebase`: https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History

Build the documentation
^^^^^^^^^^^^^^^^^^^^^^^

Without spell checking:

.. code-block:: console

    $ tox -e docs
    $ python -m webbrowser docs/_build/html/index.html

Run spell checking on the documentation:

.. code-block:: console

    $ sudo apt install enchant
    $ tox -e docs-spelling

Because of outdated software and version incompatibilities, spell checking is not
checked in the CI, and we don't require people to run it in their PR. Though, it's
always a nice thing to do. Feel free to include any spell fix in your PR, even if it's
not related to your PR (but please put it in a dedicated commit).

If you need to add words to the spell checking dictionnary, it's in
``docs/spelling_wordlist.txt``. Make sure the file is alphabetically sorted!

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
