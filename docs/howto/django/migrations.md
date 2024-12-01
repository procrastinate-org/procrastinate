# Use Procrastinate migrations with Django

Procrastinate comes with its own migrations so don't forget to run
`./manage.py migrate`.

Procrastinate provides 2 kinds of migrations:

-   The Django equivalent of the `procrastinate` normal migrations, which are
    used to create all of the PostgreSQL DDL objects used by Procrastinate.
-   Specific noop migrations used for Django to understand the Procrastinate
    Models (see {doc}`models`).

Procrastinate's Django migrations are always kept
in sync with your current version of Procrastinate, it's always a good idea
to check the release notes and read the migrations when upgrading so that you
know what will be happening to the database.

See {doc}`../production/migrations` for more information on migrations, especially
around `pre` and `post` migrations: if you deploy while the code is running, you'll
want to ensure you run the `pre-` migrations before you deploy the code and the
`post-` migrations after.
