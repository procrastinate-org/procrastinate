# Migrate the Procrastinate schema

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
xx.yy.zz_ab_very_short_description_of_the_migration.sql
```

- `xx.yy.zz` is the version of Procrastinate the migration script can be applied to.
- `ab` is the migration script's serial number, `01` being the first number in the
  series.

:::{note}
There is a [debate](https://github.com/procrastinate-org/procrastinate/issues/1040)
on whether Procrastinate should have its own migration management system or provide
directions for how to use classic ones (apart from Django), please feel free to chime in
and/or contribute code or documentation if you have an opinion on this.
:::

Let's say you are currently using Procrastinate 1.9.0, and you want to update to
Procrastinate 1.15.0. In that case, before upgrading the Procrastinate Python package
(from 1.9.0 to 1.15.0), you will need to apply all the migration scripts whose versions
are greater than or equal to 1.9.0, and lower than 1.15.0 (1.9.0 ≤ version \< 1.15.0).
And you will apply them in version order, and, for a version, in serial number order.
For example, you will apply the following migration scripts, in that order:

1. `01.09.00_01_xxxxx.sql`
2. `01.10.00_01_xxxxx.sql`
3. `01.11.00_01_xxxxx.sql`
4. `01.11.00_02_xxxxx.sql`
5. `01.12.00_01_xxxxx.sql`
6. `01.14.00_01_xxxxx.sql`
7. `01.14.00_02_xxxxx.sql`

If you want to upgrade from one Procrastinate major version to another, say from
Procrastinate 1.6.0 to 3.2.0, there are two options, depending on whether you can
interrupt the service to do the migration or not.

## The easier way, with service interruption

1. Shut down the services that use Procrastinate: both the services that defer tasks and
   the workers.
2. Apply all the migration scripts (1.6.0 ≤ version \< 3.2.0).
3. Upgrade your code to the new Procrastinate version (3.2.0).
4. Start all the services.

This, as you've noticed, only works if you're able to stop the services.

## The safer way, without service interruption

:::{note}
This only applies starting at Procrastinate 0.17.0. For previous versions,
you will have to interrupt the service or write custom migrations.
:::

If you care about service continuity, you'll need to make intermediate upgrades. For
example, to upgrade from Procrastinate 1.6.0 to 3.2.0, here are the steps you will need
to follow:

1. Apply all the migration scripts between 1.6.0 and 2.0.0 (1.6.0 ≤ version \< 2.0.0).
2. Live-upgrade the Procrastinate version used in your services, from 1.6.0 to 2.0.0.
3. Apply all the migration scripts between 2.0.0 and 3.0.0 (2.0.0 ≤ version \< 3.0.0).
4. Live-upgrade the Procrastinate version used in your services, from 2.0.0 to 3.0.0.
5. Apply all the migration scripts between 3.0.0 and 3.2.0 (3.0.0 ≤ version \< 3.2.0).
6. Live-upgrade the Procrastinate version used in your services, from 3.0.0 and 3.2.0.

Following this process you can go from 1.6.0 to 3.2.0 with no service discontinuity.
