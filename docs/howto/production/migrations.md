# Migrate the Procrastinate schema

:::{warning}
v3 introduces a new way to handle migrations. Hopefully, easier both for users
and maintainers. Read about pre- and post-migrations below.
:::

When the Procrastinate database schema evolves in new Procrastinate releases, new
migrations are released alongside. Look at the
[Release notes](https://github.com/procrastinate-org/procrastinate/releases)
for a listing of new migrations for each release.

Migrations are SQL scripts that can be executed on the DB before the release and
apply the changes needed to get to the new schema.

Here's an example of a migration script:

```sql
ALTER TABLE procrastinate_jobs ADD COLUMN extra TEXT;
```

The migration scripts are pure-SQL scripts, meaning that they may be applied to the
database using any PostgreSQL client, including `psql` and `PGAdmin`.

:::{note}
If you use Django, instead of using the SQL migration scripts directly, you way want
to rely on the Procrastinate Django app, and the Django database migration scripts
this app provides. See {doc}`../django/migrations` for more information.
:::

The migration scripts are located in the `procrastinate/sql/migrations` directory of
the Procrastinate Git repository. They're also shipped in the Python packages published
on PyPI. A simple way to list all the migrations is to use the command:

```console
$ procrastinate schema --migrations-path
/home/me/my_venv/lib/python3.x/lib/site-packages/procrastinate/sql/migrations
```

It's your responsibility to keep track of which migrations have been applied yet
or not. Thankfully, the names of procrastinate migrations should help you: they
follow a specific pattern:

```
{xx.yy.zz}_{ab}_{pre|post}_very_short_description_of_the_migration.sql
```

-   `xx.yy.zz` is the version of Procrastinate the migration script can be applied to.
-   `ab` is the migration script's serial number, `01` being the first number in the
    series.
-   `pre` / `post`: indicates wether the migration should be applied before
    upgrading the code (`pre`) or after upgrading the code (`post`) in the context
    of a blue-green deployment. On old migrations, if `pre` or `post` is not
    specified, it's a `post` migration.

:::{note}
There is a [debate](https://github.com/procrastinate-org/procrastinate/issues/1040)
on whether Procrastinate should have its own migration management system or provide
directions for how to use classic ones (apart from Django), please feel free to chime in
and/or contribute code or documentation if you have an opinion on this.
:::

## How to apply migrations

### The easier way, with service interruption

1. Shut down the services that use Procrastinate: both the services that defer tasks and
   the workers.
2. Apply all the migration scripts (`pre` & `post`), e.g. with:

```console
$ MIGRATION_TO_APPLY="02.00.00_01_pre_some_migration.sql"
$ cat $(procrastinate schema --migrations-path)/${MIGRATION_TO_APPLY} | psql
$ MIGRATION_TO_APPLY="02.00.00_01_post_some_migration.sql"
$ cat $(procrastinate schema --migrations-path)/${MIGRATION_TO_APPLY} | psql
$ ...
```

3. Upgrade your code to the new Procrastinate version.
4. Start all the services.

This, as you've noticed, only works if you're able to stop the services.

### The safer way, without service interruption

If you need to ensure service continuity, you'll need to make intermediate upgrades.
Basically, you'll need to stop at every version that provides migrations.

```console
$ MIGRATION_TO_APPLY="02.01.00_01_pre_some_migration.sql"
$ cat $(procrastinate schema --migrations-path)/${MIGRATION_TO_APPLY} | psql

$ yoursystem/deploy procrastinate 2.1.0

$ MIGRATION_TO_APPLY="02.01.00_01_post_some_migration.sql"
$ cat $(procrastinate schema --migrations-path)/${MIGRATION_TO_APPLY} | psql

$ MIGRATION_TO_APPLY="02.02.00_01_pre_some_migration.sql"
$ cat $(procrastinate schema --migrations-path)/${MIGRATION_TO_APPLY} | psql

$ yoursystem/deploy procrastinate 2.2.0

$ MIGRATION_TO_APPLY="02.02.00_01_post_some_migration.sql"
$ cat $(procrastinate schema --migrations-path)/${MIGRATION_TO_APPLY} | psql
```
