Contributing
============

You're welcome to come and procrastinate with us :)

This contributing guide is trying to avoid common pitfalls, but the project
development environment is quite common. If it's not your first rodeo, here's a TL;DR

TL;DR
-----

(The following is not meant to be executed as a script)

.. code-block:: console

    $ # Export libpq env vars for PG connection
    $ export PGDATABASE=procrastinate PGHOST=localhost PGUSER=postgres

    $ # Launch PostgreSQL within Docker
    $ docker-compose up -d

    $ # Explore tox entrypoints
    $ tox -l

    $ # You can do things without tox too:

    $ # Install requirements
    $ pip install -r requirements.txt

    $ # Launch tests
    $ pytest

    $ # Launch demo
    $ export PROCRASTINATE_APP=procrastinate_demo.app.app
    $ procrastinate -h

Instructions for contribution
-----------------------------

Environment variables
^^^^^^^^^^^^^^^^^^^^^

The `export` command below will be necessary whenever you want to interact with
the database (using the project locally, launching tests, ...).
These are standard ``libpq`` environment variables, and the values used below correspond
to the docker setup. Feel free to adjust them as necessary.

.. code-block:: console

    $ export PGDATABASE=procrastinate PGHOST=localhost PGUSER=postgres

Create your development database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The development database can be launched using docker with a single command.
The PostgreSQL database we used is a fresh standard out-of-the-box database
on the latest stable version.

.. code-block:: console

    $ docker-compose up -d

If you want to try out the project locally, it's useful to have ``postgresql-client``
installed. It will give you both a PostgreSQL console (``psql``) and specialized
commands like ``createdb`` we use below.

.. code-block:: console

    $ sudo apt install postgresql-client
    $ createdb

Set up your development environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't plan to run the code interactively and just want to run tests,
linting and build the doc, you'll just need ``tox``. You can install it
for your user:

.. code-block:: console

    $ pip install --user tox

In order for this to work, you'll need to make sure your python user install binary
directory is included in your shell's ``PATH``. One way of doing that is to add
a line in your ``~/.profile`` (or ``~/.zprofile`` for ``zsh``). The following command
will output the line to write in that file:

.. code-block:: console

    echo "export PATH=$(python3 -c "import site; print(site.USER_BASE)")/bin:"'$PATH'

If you plan to launch the project locally, install the package itself with development
dependencies in a virtual environment:

.. code-block:: console

    $ python3 -m venv .venv
    $ source .venv/bin/activate

You can check that your Python environment is properly activated:

.. code-block:: console

    (venv) $ which python
    /path/to/current/folder/.venv/bin/python

Install local dependencies:

.. code-block:: console

    (venv) $ pip install -r requirements.txt

Run the project automated tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With a running database:

.. code-block:: console

    (venv) $ pytest  # Test the code with the current interpreter

Or

.. code-block:: console

    $ tox  # Run all the checks for all the interpreters

If you're not familiar with Pytest_, do yourself a treat and look into this fabulous
tool.

.. _Pytest: https://docs.pytest.org/en/latest/

If you don't know Tox_, have a look at their documentation, it's a very nice tool too.

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

You can also install a `pre-commit`
hook which makes sure that all your commits are created clean:

.. code-block:: console

    cat > .git/hooks/pre-commit <<EOF
    #!/bin/bash -e
    exec ./pre-commit-hook
    EOF
    chmod +x .git/hooks/pre-commit

If ``tox`` is installed inside your ``virtualenv``, you may want to activate the
``virtualenv`` in ``.git/hooks/pre-commit``:

.. code-block:: bash

    #!/bin/bash -e
    source /path/to/venv/bin/activate
    exec ./pre-commit-hook

This will keep you from creating a commit if there's a linting problem.

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

If you need to add words to the spell checking dictionary, it's in
``docs/spelling_wordlist.txt``. Make sure the file is alphabetically sorted!

Migrations
----------

Create database migration scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you make changes to the database structure (``procrastinate/sql/schema.sql``) you
also need to create a corresponding migration script in the
``procrastinate/sql/migrations`` directory.

For example, let's say you want to add column named ``extra`` to the
``procrastinate_jobs`` table. You would obviously edit ``procrastinate/sql/schema.sql``
and change the definition of the table to add that column. But you'd also need to create
a migration script, whose content would look like this:

.. code-block:: sql

    -- add a column extra to the procrastinate_jobs table
    ALTER TABLE procrastinate_jobs ADD COLUMN extra TEXT;

The name of migration scripts must follow a specific pattern:

.. code-block::

    delta_x.y.z_abc_very_short_description_of_your_changes.sql

We follow the conventions and rules of the `Pum`_ (PostgreSQL Updates Manager) project.

.. _`Pum`: https://github.com/opengisch/pum/

``x.y.z`` is the number of the latest released version of Procrastinate. (The latest
release is the one marked ``Latest release`` on the `Procrastinate releases`_ page.)
``abc`` is the migration script's serial number, ``001`` being the first number in the
series. And, finally, ``very_short_description_of_your_changes`` is a very short
description of the changes. It is important to use underscores between the different
parts, and between words in the short description.

.. _`Procrastinate releases`: https://github.com/peopledoc/procrastinate/releases

For example, let's say the latest released version of Procrastinate is ``1.0.1``, and
that the ``migrations`` directory already includes a migration script whose serial
number is ``001`` for that release number. In that case, if you need to add a migration
script, its name will start with ``delta_1.0.1_002_``.

Try our demo
------------

With a running database:

Launch a worker with:

.. code-block:: console

    (venv) $ export PROCRASTINATE_APP=procrastinate_demo.app.app
    (venv) $ procrastinate schema --apply
    (venv) $ procrastinate worker

Schedule some tasks with:

.. code-block:: console

    (venv) $ python -m procrastinate_demo

Wait, there are ``async`` and ``await`` keywords everywhere!?
-------------------------------------------------------------

Yes, in order to provide both a synchronous **and** asynchronous API, Procrastinate
needs to be asynchronous at core.

We're using a trick to avoid implementing two almost identical APIs for synchronous
and asynchronous usage. Find out more in the documentation, in the Discussions
section. If you need information on how to work with asynchronous Python, check out:

- The official documentation: https://docs.python.org/3/library/asyncio.html
- A more accessible guide by Brad Solomon: https://realpython.com/async-io-python/


Release a new version
---------------------

Prepare a changelog in a drafted GitHub release, and then release it, with a tag.
That's it.

The tag will be seen by Travis, that will then create a release (using the tag as
version number, thanks to our ``setup.py``), and push it to PyPI (using the new API
tokens and an environment variable). That build should also trigger a ReadTheDocs
build, which will read GitHub releases (thanks to our ``changelog`` extension) and
write a proper changelog in the published documentation.
