Contributing
============

You're welcome to come and procrastinate with us :)

TL;DR
-----

.. code-block:: console

    $ source ./dev-env

Of course, feel free to read the script before launching it.

This script is intended to be a one-liner that sets up everything you need. It makes
the following assumptions:

- You're using ``MacOS`` or ``Linux``, and ``bash`` or ``zsh``.
- You already have ``python3`` available
- You either have ``virtualenv`` installed or your ``python3`` supports ``-m venv``
  (on Ubuntu, ``sudo apt install python3-venv``)
- Either you've already created a ``virtualenv``, or you're OK with the script creating
  a local ``virtualenv`` in ``.venv``
- Either you've already setup a PostgreSQL database and environment variables (``PG*``)
  are set or you have ``docker-compose`` available and port 5432 is free.
- Either ``psql`` and other ``libpq`` executables are available in the ``PATH`` or they
  are located in ``usr/local/opt/libpq/bin`` (``Homebrew``).

Instructions for contribution
-----------------------------

Environment variables
^^^^^^^^^^^^^^^^^^^^^

The ``export`` command below will be necessary whenever you want to interact with
the database (using the project locally, launching tests, ...).
These are standard ``libpq`` environment variables, and the values used below correspond
to the Docker setup. Feel free to adjust them as necessary.

.. code-block:: console

    $ export PGDATABASE=procrastinate PGHOST=localhost PGUSER=postgres PGPASSWORD=password

Create your development database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The development database can be launched using Docker with a single command.
The PostgreSQL database we used is a fresh standard out-of-the-box database
on the latest stable version.

.. code-block:: console

    $ docker-compose up -d postgres

If you want to try out the project locally, it's useful to have ``postgresql-client``
installed. It will give you both a PostgreSQL console (``psql``) and specialized
commands like ``createdb`` we use below.

.. code-block:: console

    $ # Ubuntu
    $ sudo apt install postgresql-client
    $ createdb

.. code-block:: console

    $ # MacOS
    $ brew install libpq
    $ /usr/local/opt/libpq/bin/createdb

Set up your development environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install the package itself with development dependencies in a virtual environment:

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

You can also install a ``pre-commit``
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

In addition, an editorconfig_ file will help your favorite editor to respect
procrastinate coding style. It is automatically used by most famous IDEs, such as
Pycharm and VS Code.

.. _editorconfig: https://editorconfig.org/

Build the documentation
^^^^^^^^^^^^^^^^^^^^^^^

Build with:

.. code-block:: console

    $ tox -e docs
    $ python -m webbrowser docs/_build/html/index.html

Run spell checking on the documentation (optional):

.. code-block:: console

    $ sudo apt install enchant
    $ tox -e docs-spelling

Because of outdated software and version incompatibilities, spell checking is not
checked in the CI, and we don't require people to run it in their PR. Though, it's
always a nice thing to do. Feel free to include any spell fix in your PR, even if it's
not related to your PR (but please put it in a dedicated commit).

If you need to add words to the spell checking dictionary, it's in
``docs/spelling_wordlist.txt``. Make sure the file is alphabetically sorted.

If Sphinx's console output is localized and you would rather have it in English,
use the environment variable ``LC_ALL=C.utf-8`` (either exported or attached to the
tox process)

Migrations
----------

Create database migration scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you make changes to the database structure (``procrastinate/sql/schema.sql``) you
also need to create a corresponding migration script in the
``procrastinate/sql/migrations`` directory.

For example, let's say you want to add a column named ``extra`` to the
``procrastinate_jobs`` table. You will first edit ``procrastinate/sql/schema.sql`` and
change the definition of the table to add that column. That would be sufficient for new
Procrastinate users, but existing users, whose database already includes Procrastinate
objects (tables, indexes, ...), need to be able to migrate their existing schema into
the new one. For that reason, as a Procrastinate developer, you'll also need to create
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

Migration tests
^^^^^^^^^^^^^^^

The continuous integration contains tests that will check that the schema and the
migrations succeed in producing the same database structure. Run these tests locally
with:

.. code-block:: console

    $ tox -e py38-migration-tests

Try our demo
------------

With a running database, and its schema installed:

.. code-block:: console

    (venv) $ export PROCRASTINATE_APP=procrastinate_demo.app.app
    (venv) $ procrastinate schema --apply

schedule some tasks with a script:

.. code-block:: console

    (venv) $ python -m procrastinate_demo

Or from the command line:

.. code-block:: console

    procrastinate defer procrastinate_demo.tasks.sum '{"a": 3, "b": 5}'
    procrastinate defer procrastinate_demo.tasks.sum '{"a": 5, "b": 7}'
    procrastinate defer procrastinate_demo.tasks.sum '{"a": 5, "b": "}")'
    procrastinate defer procrastinate_demo.tasks.sum_plus_one '{"a": 4, "b": 7}'
    procrastinate defer --lock a procrastinate_demo.tasks.sleep '{"i": 2}'
    procrastinate defer --lock a procrastinate_demo.tasks.sleep '{"i": 3}'
    procrastinate defer --lock a procrastinate_demo.tasks.sleep '{"i": 4}'
    procrastinate defer procrastinate_demo.tasks.random_fail '{}'

Launch a worker with:

.. code-block:: console

    (venv) $ procrastinate worker


Use Docker for Procrastinate development
----------------------------------------

In the development setup described above, Procrastinate, its dependencies, and the
development tools (``tox``, ``black``, ``pytest``, etc.) are installed in a virtual
Python environment on the host system. Alternatively, they can be installed in a Docker
image, and Procrastinate and all the development tools can be run in Docker containers.
Docker is useful when you can't, or don't want to, install System requirements such as
the ``libpq-dev`` package (required by the ``psycopg2`` dependency).

This section shows, through ``docker-compose`` command examples, how to test and run
Procrastinate in Docker.

Build the ``procrastinate`` Docker image:

.. code-block:: console

    $ docker-compose build procrastinate

Run the automated tests:

.. code-block:: console

    $ export UID
    $ export GID=$(id -g)
    $ docker-compose run --rm procrastinate pytest

Docker Compose is configured (in ``docker-compose.yml``) to mount the local directory on
the host system onto ``/procrastinate_dev`` in the container. This means that local
changes made to the Procrastinate code are visible in Procrastinate containers.

The ``UID`` and ``GID`` environment variables are set and exported for the Procrastinate
container to be run with the current user id and group id. If not set or exported, the
Procrastinate container will run as root, and files owned by root may be created in the
developer's working directory.

In the definition of the ``procrastinate`` service in ``docker-compose.yml`` the
``PROCRASTINATE_APP`` variable is set to ``procrastinate_demo.app.app`` (the
Procrastinate demo application). So ``procrastinate`` commands run in Procrastinate
containers are always run as if they were passed ``--app procrastinate_demo.app.app``.

Run the ``procrastinate`` command :

.. code-block:: console

    $ docker-compose run --rm procrastinate procrastinate -h

Apply the Procrastinate database schema:

.. code-block:: console

    $ docker-compose run --rm procrastinate procrastinate schema --apply

Run the Procrastinate healthchecks:

.. code-block:: console

    $ docker-compose run --rm procrastinate procrastinate healthchecks

Start a Procrastinate worker (``-d`` used to start the container in detached mode):

.. code-block:: console

    $ docker-compose up -d procrastinate

Run a command (``bash`` here) in the Procrastinate worker container just started:

.. code-block:: console

    $ docker-compose exec procrastinate bash

Watch the Procrastinate worker logs:

.. code-block:: console

    $ docker-compose logs -ft procrastinate

Use the ``procrastinate defer`` command to create a job:

.. code-block:: console

    $ docker-compose run --rm procrastinate procrastinate defer procrastinate_demo.tasks.sum '{"a":3, "b": 5}'

Or run the demo main file:

.. code-block:: console

    $ docker-compose run --rm procrastinate python -m procrastinate_demo

Stop and remove all the containers (including the ``postgres`` container):

.. code-block:: console

    $ docker-compose down

Wait, there are ``async`` and ``await`` keywords everywhere!?
-------------------------------------------------------------

Yes, in order to provide both a synchronous **and** asynchronous API, Procrastinate
needs to be asynchronous at core.

We're using a trick to avoid implementing two almost identical APIs for synchronous
and asynchronous usage. Find out more in the documentation, in the Discussions
section. If you need information on how to work with asynchronous Python, check out:

- The official documentation: https://docs.python.org/3/library/asyncio.html
- A more accessible guide by Brad Solomon: https://realpython.com/async-io-python/

Core contributor additional documentation
-----------------------------------------

Issues
^^^^^^

Please remember to tag Issues with appropriate labels.

Pull Requests
^^^^^^^^^^^^^

PR labels help ``release-drafter`` pre-fill the next release draft. They're not
mandatory, but releasing will be easier if they're present.

Release a new version
^^^^^^^^^^^^^^^^^^^^^

There should be an active Release Draft with the changelog in GitHub releases. Make
relevant edits to the changelog, (see ``TODO``) including listing the migrations
for the release. Click on Release, that's it, the rest is automated.

When creating the release, GitHub will save the release info and create a tag with
the provided version. The new tag will be seen by Github Actions, which will then
create a wheel (using the tag as version number, thanks to our ``setup.py``), and push
it to PyPI (using the new API tokens). That tag should also trigger a ReadTheDocs
build, which will read GitHub releases (thanks to our ``changelog`` extension)
which will  write the changelog in the published documentation (transformed from
``Markdown`` to ``RestructuredText``).
