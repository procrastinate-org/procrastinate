Use Pum for schema migrations
-----------------------------

When Procrastinate developers make changes to the Procrastinate database schema they
write migration scripts.

Here's an example of a migration script:

.. code-block:: sql

    ALTER TABLE procrastinate_jobs ADD COLUMN extra TEXT;

Migration scripts are pure-SQL scripts, meaning that they may be applied to the database
using any PostgreSQL client, including ``psql`` and ``PGAdmin``.

The names of migration script files adhere to a certain pattern, which comes from the
`Pum`_ project. Pum is thus a good choice for Procrastinate migrations, although other
migration tools may be used as well.

See the `Pum README`_ on GitHub to know how to use Pum. But below is a Pum quickstart,
applied to Procrastinate.

First of all, note that Pum connects to the PostgreSQL database using a `PostgreSQL
Connection Service`_. So you have to have a Connection Service File. Here's an example
of a Connection Service File (located at ``~/.pg_service.conf``):

.. code-block::

    [procrastinate]
    host=localhost
    port=5432
    user=postgres
    password=xxxxxxx
    dbname=procrastinate

You can use ``psql service=procrastinate`` to check that you can connect to
PostgreSQL through the ``procrastinate`` service defined in your Connection Service
File.

The first time you install Procrastinate you will need to apply the Procrastinate schema
to the database using the ``procrastinate schema --apply`` command.

If you decide to use Pum for handling migrations you'll also need to create the Pum
table (which Pum uses internally for tracking schema versions), and set the ``baseline``
in this table.

Let's say you are installing Procrastinate 0.5.0. Your baseline will then be 0.5.0. This
the Pum command to set the baseline:

.. code-block:: console

    pum baseline --pg_service procrastinate --table public.pum --dir $(procrastinate schema --migrations-path) --baseline 0.5.0

* ``--pg_service`` specifies the PostgreSQL Connection Service to use
* ``--table`` specifies the name of the Pum table to create and insert the baseline into
  (the table name must be prefixed by the schema name)
* ``--dir`` specifies the path of the directory including migration scripts (it is
  not relevant here, yet mandatory)
* ``--baseline`` specifies the version number to use for the baseline

.. note::

    The command ``procastinate schema --migrations-path`` is not available with
    Procrastinate <= 0.5.0. So you'll have to find the path to the migrations directory
    (``sql/migrations`` within the ``site-packages/procrastinate`` directory).

You're all set at this point! Procrastinate is ready to use, and your Pum baseline is
set for future migrations of the Procrastinate schema.

Now let's say you want to upgrade from Procrastinate 0.5.0 to 0.6.0. You will install
Procrastinate 0.6.0 in your Python environment (for example using ``pip``), and you will
then use Pum to apply the necessary migration scripts, that is the migration scripts the
Procrastinate developers created for migrating from the 0.5.0 version of Procrastinate.

This is how migration scripts are applied using Pum:

.. code-block:: console

    pum upgrade --pg_service procrastinate --table public.pum --dir $(procrastinate schema --migrations-path)

The ``--pg_service``, ``--table``, and ``--dir`` flags have been described above, in the
context of the ``pum baseline`` command.

The output of the ``pum upgrade`` command should look like this:

.. code-block:: console

    Upgrade...
    Applying delta 0.5.0 001_drop_started_at_column... OK
    Applying delta 0.5.0 002_drop_started_at_column... OK
    Applying delta 0.5.0 003_drop_procrastinate_version_table... OK

In this example ``pum upgrade`` applied three migration scripts, two related to
the dropping a column and one related to the dropping of a table.

That is all! Pum includes other commands, check commands for verifying migrations in
particular. Check out the Pum documentation for more information.

.. _`Pum`: https://github.com/opengisch/pum/
.. _`Pum README`: https://github.com/opengisch/pum/blob/master/README.md
.. _`PostgreSQL Connection Service`: https://www.postgresql.org/docs/current/libpq-pgservice.html
