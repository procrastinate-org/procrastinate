Migrate the Procrastinate schema
--------------------------------

When Procrastinate developers make changes to the Procrastinate database schema
they write migration scripts.

Here's an example of a migration script:

.. code-block:: sql

     ALTER TABLE procrastinate_jobs ADD COLUMN extra TEXT;

The migration scripts are pure-SQL scripts, meaning that they may be applied to the
database using any PostgreSQL client, including ``psql`` and ``PGAdmin``.

.. note::

    If you use Django, instead of using the SQL migration scripts directly, you way want
    to rely on the Procrastinate Django app, and the Django database migration scripts
    this app provides. See `django` for more information.

The migration scripts are located in the ``procrastinate/sql/migrations`` directory of
the Procrastinate Git repository. They're also shipped in the Python packages published
on PyPI.

The names of migration script files adhere to a certain pattern:

.. code-block::

    delta_x.y.z_abc_very_short_description_of_your_changes.sql

* ``x.y.z`` is the version of Procrastinate the migration script can be applied to.
* ``abc`` is the migration script's serial number, ``001`` being the first number in the
  series.
* ``very_short_description_of_your_changes`` is a very short description of the
  migration.

Let's say you are currently using Procrastinate 0.9.0, and you want to update to
Procrastinate 0.15.0. In that case you will need to apply all the migration scripts
whose versions are greater than or equal to 0.9.0, and lower than 0.15.0 (0.9.0
≤ version < 0.15.0). And you will apply them in version order, and, for a version, in
serial number order. For example, you will apply the following migration scripts, in
that order:

1. ``delta_0.9.0_001_xxxxx.sql``
2. ``delta_0.10.0_001_xxxxx.sql``
3. ``delta_0.11.0_001_xxxxx.sql``
4. ``delta_0.11.0_002_xxxxx.sql``
5. ``delta_0.12.0_001_xxxxx.sql``
6. ``delta_0.14.0_001_xxxxx.sql``
7. ``delta_0.14.0_002_xxxxx.sql``

.. note::

    The ordering of migrations scripts is not based on the typical lexicographical
    order. For example, ``delta_0.9.0_001_xxxxx.sql`` is to be applied before
    ```delta_0.10.0_001_xxxxx.sql`` (because version 0.9.0 is lower than
    0.10.0).
