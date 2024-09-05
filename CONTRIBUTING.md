# Contributing

You're welcome to come and procrastinate with us :)

## TL;DR

```console
$ source ./dev-env
```

Of course, feel free to read the script before launching it.

This script is intended to be a one-liner that sets up everything you need. It makes
the following assumptions:

-   You're using `MacOS` or `Linux`, and `bash` or `zsh`.
-   You already have `python3` available
-   You have `poetry` [installed](https://python-poetry.org/docs/#installation)
-   Either you've already setup a PostgreSQL database and environment variables (`PG*`)
    are set or you have `docker compose` available and port 5432 is free.
-   Either `psql` and other `libpq` executables are available in the `PATH` or they
    are located in `usr/local/opt/libpq/bin` (`Homebrew`).

The `dev-env` script will add the `scripts` folder to your `$PATH` for the current
shell, so in the following documentation, if you see `scripts/foo`, you're welcome
to call `foo` directly.

## Instructions for contribution

### Environment variables

The `export` command below will be necessary whenever you want to interact
with the database (using the project locally, launching tests, ...). These are
standard [libpq environment variables] environment variables, and the values
used below correspond to the Docker setup. Feel free to adjust them as
necessary (The `dev-env` script will set them for you).

```console
$ export PGDATABASE=procrastinate PGHOST=localhost PGUSER=postgres PGPASSWORD=password
```

### Create your development database

The development database can be launched using Docker with a single command.
The PostgreSQL database we used is a fresh standard out-of-the-box database
on the latest stable version.

```console
$ docker compose up -d postgres
```

If you want to try out the project locally, it's useful to have `postgresql-client`
installed. It will give you both a PostgreSQL console (`psql`) and specialized
commands like `createdb` we use below.

```console
$ # Ubuntu
$ sudo apt install postgresql-client
$ createdb
```

```console
$ # MacOS
$ brew install libpq
$ /usr/local/opt/libpq/bin/createdb
```

### Set up your development environment

The development environment is managed by [poetry]. It's a tool that manages
dependencies and virtual environments. We also use [pre-commit] to keep the code
clean.

If you don't already have `poetry` or `pre-commit` installed, you can
install them with:

```console
$ scripts/bootstrap
```

This will install [pipx] if necessary and use it to install `poetry` and
`pre-commit`.

Then, install Procrastinate with development dependencies in a virtual environment:

```console
$ poetry env use 3.{x}  # Select the Python version you want to use (replace {x})
$ poetry install
$ poetry shell  # Activate the virtual environment
```

You can check that your Python environment is properly activated:

```console
(venv) $ which python
/path/to/current/folder/.venv/bin/python
```

### Run the project automated tests

With a running database:

```console
(venv) $ pytest  # Test the code with the current interpreter
```

If you're not familiar with [Pytest], do yourself a treat and look into this fabulous
tool.

To look at coverage in the browser after launching the tests, use:

```console
$ scripts/htmlcov
```

### Keep your code clean

This project uses [pre-commit] to keep the code clean. It's a tool that runs
automated checks on your code before you commit it. Install the pre-commit
hooks with:

```console
$ pre-commit install
```

This will keep you from creating a commit if there's a linting problem.

In addition, an [editorconfig] file will help your favorite editor to respect
procrastinate coding style. It is automatically used by most famous IDEs, such as
Pycharm and VS Code.

### Write the documentation

The documentation is written in `Markdown` and built with `Sphinx` and `MyST`.
Docstrings are written in `reStructuredText` (because writing them in `MyST` is
still a bit complicated, it seems).

### Build the documentation

Build with:

```console
$ scripts/docs  # build the html doc
$ scripts/htmldoc  # browse the doc in you browser
```

If Sphinx's console output is localized and you would rather have it in English,
(which make google-based debugging much easier), use the environment variable
`export LC_ALL=C.utf-8`

## Migrations

### Create database migration scripts

If you make changes to the database structure (`procrastinate/sql/schema.sql`) you
also need to create a corresponding migration script in the
`procrastinate/sql/migrations` directory.

For example, let's say you want to add a column named `extra` to the
`procrastinate_jobs` table. You will first edit `procrastinate/sql/schema.sql` and
change the definition of the table to add that column. That would be sufficient for new
Procrastinate users, but existing users, whose database already includes Procrastinate
objects (tables, indexes, ...), need to be able to migrate their existing schema into
the new one. For that reason, as a Procrastinate developer, you'll also need to create
a migration script, whose content would look like this:

```sql
-- add a column extra to the procrastinate_jobs table
ALTER TABLE procrastinate_jobs ADD COLUMN extra TEXT;
```

The name of migration scripts must follow a specific pattern:

```
xx.yy.zz_ab_very_short_description_of_your_changes.sql
```

`xx.yy.zz` is the number of the latest released version of Procrastinate. (The latest
release is the one marked `Latest release` on the [Procrastinate releases] page.)
`xx`, `yy` and `zz` must be 2-digit numbers, with leading zeros if necessary.
`ab` is the 2-digit migration script's serial number, `01` being the first number in
the series. And, finally, `very_short_description_of_your_changes` is a very short
description of the changes (wow). It is important to use underscores between the
different parts, and between words in the short description.

For example, let's say the latest released version of Procrastinate is `1.0.1`, and
that the `migrations` directory already includes a migration script whose serial
number is `01` for that release number. In that case, if you need to add a migration
script, its name will start with `01.00.01_02_`.

### Backward-compatibility

As a Procrastinate developer, the changes that you make to the Procrastinate database
schema must be compatible with the Python code of previous Procrastinate versions.

For example, let's say that the current Procrastinate database schema includes an SQL
function

```sql
procrastinate_func(arg1 integer, arg2 text, arg3 timestamp)
```

that you want to change to

```sql
procrastinate_func(arg1 integer, arg2 text)
```

The straightforward way to do that would be to edit the `schema.sql` file and just
replace the old function by the new one, and add a migration script that removes the old
function and adds the new one:

```sql
DROP FUNCTION procrastinate_func(integer, text, timestamp);
CREATE FUNCTION procrastinate_func(arg1 integer, arg2 text)
RETURNS INT
...
```

But if you do that you will break the Procrastinate Python code that uses the old
version of the `procrastinate_func` function. The direct consequence of that is
that Procrastinate users won't be able to upgrade Procrastinate without incurring
a service outage.

So when you make changes to the Procrastinate database schema you must ensure that the
new schema still works with old versions of the Procrastinate Python code.

Going back to our `procrastinate_func` example. Instead of replacing the old function
by the new one in `schema.sql`, you will leave the old function, and just add the new
one. And your migration script will just involve adding the new version of the function:

```sql
CREATE FUNCTION procrastinate_func(arg1 integer, arg2 text)
RETURNS INT
...
```

The question that comes next is: when can the old version of `procrastinate_func` be
removed? Or more generally, when can the SQL compatibility layer be removed?

The answer is some time after the next major version of Procrastinate!

For example, if the current Procrastinate version is 1.5.0, the SQL compatibility layer
will be removed after 2.0.0 is released. The 2.0.0 release will be a pivot release, in
the sense that Procrastinate users who want to upgrade from, say, 1.5.0 to 2.5.0, will
need to upgrade from 1.5.0 to 2.0.0 first, and then from 2.0.0 to 2.5.0. And they will
always migrate the database schema before updating the code.

The task of removing the SQL compatibility layer after the release of a major version
(e.g. 2.0.0) is the responsibility of Procrastinate maintainers. More specifically, for
the 2.1.0 release, Procrastinate maintainers will need to edit `schema.sql` and remove
the SQL compatibility layer.

But, as a standard developer, when you make changes to the Procrastinate database schema
that involves leaving or adding SQL statements for compatibility reasons, it's a good
idea to add a migration script for the removal of the SQL compatibility layer. This will
greatly help the Procrastinate maintainers.

For example, let's say the current released version of Procrastinate is 1.5.0, and you
want to change the signature of `procrastinate_func` as described above. You will add
a `1.5.0` migration script (e.g.
`01.05.00_01_add_new_version_procrastinate_func.sql`) that adds the new version of
the function, as already described above. And you will also add a `2.0.0` migration
script (e.g. `02.00.00_01_remove_old_version_procrastinate_func.sql`) that takes
care of removing the old version of the function:

```sql
DROP FUNCTION procrastinate_func(integer, text, timestamp);
```

In this way, you provide the new SQL code, the compatibility layer, and the migration
for the removal of the compatibility layer.

:::{note}
The migration scripts that remove the SQL compatibility code are to be added to the
`future_migrations` directory instead of the `migrations` directory. And it will
be the responsibility of Procrastinate maintainers to move them to the
`migrations` directory after the next major release.
:::

### Migration tests

The continuous integration contains tests that will check that the schema and the
migrations succeed in producing the same database structure. The migration tests are
included in the normal test suite, but you can run them specifically with:

```console
(venv) $ pytest tests/migration
```

## Try our demos

See the demos page for instructions on how to run the demos ({doc}`demos`).

## Use Docker for Procrastinate development

In the development setup described above, Procrastinate, its dependencies, and the
development tools (`tox`, `black`, `pytest`, etc.) are installed in a virtual
Python environment on the host system. Alternatively, they can be installed in a Docker
image, and Procrastinate and all the development tools can be run in Docker containers.
Docker is useful when you can't, or don't want to, install system requirements.

This section shows, through `docker compose` command examples, how to test and run
Procrastinate in Docker.

Build the `procrastinate` Docker image:

```console
$ export UID GID
$ docker compose build procrastinate
```

Run the automated tests:

```console
$ docker compose run --rm procrastinate pytest
```

Docker Compose is configured (in `docker compose.yml`) to mount the local directory on
the host system onto `/src` in the container. This means that local
changes made to the Procrastinate code are visible in Procrastinate containers.

The `UID` and `GID` environment variables are set and exported for the Procrastinate
container to be run with the current user id and group id. If not set or exported, the
Procrastinate container will run as root, and files owned by root may be created in the
developer's working directory.

In the definition of the `procrastinate` service in `docker compose.yml` the
`PROCRASTINATE_APP` variable is set to `procrastinate_demo.app.app` (the
Procrastinate demo application). So `procrastinate` commands run in Procrastinate
containers are always run as if they were passed `--app procrastinate_demo.app.app`.

Run the `procrastinate` command :

```console
$ docker compose run --rm procrastinate procrastinate -h
```

Apply the Procrastinate database schema:

```console
$ docker compose run --rm procrastinate procrastinate schema --apply
```

Run the Procrastinate healthchecks:

```console
$ docker compose run --rm procrastinate procrastinate healthchecks
```

Start a Procrastinate worker (`-d` used to start the container in detached mode):

```console
$ docker compose up -d procrastinate
```

Run a command (`bash` here) in the Procrastinate worker container just started:

```console
$ docker compose exec procrastinate bash
```

Watch the Procrastinate worker logs:

```console
$ docker compose logs -ft procrastinate
```

Use the `procrastinate defer` command to create a job:

```console
$ docker compose run --rm procrastinate procrastinate defer procrastinate_demo.tasks.sum '{"a":3, "b": 5}'
```

Or run the demo main file:

```console
$ docker compose run --rm procrastinate python -m procrastinate_demo
```

Stop and remove all the containers (including the `postgres` container):

```console
$ docker compose down
```

## Wait, there are `async` and `await` keywords everywhere!?

Yes, in order to provide both a synchronous **and** asynchronous API, Procrastinate
needs to be asynchronous at core.

When possible, we're trying to avoid duplicating code, with designs such as
["hoisting the I/O"](https://www.youtube.com/watch?v=PBQN62oUnN8).

## Core contributor additional documentation

### Issues

Please remember to tag Issues with appropriate labels.

### Pull Requests

PR labels help pre-filling the next release draft. They're not
mandatory, but releasing will be easier if they're present.

### Release a new version

Draft a new release, Generate release notes, add `## Migrations`. Make relevant
edits to the changelog, (see `TODO`). Click on Release, that's it, the rest is
automated. This works with pre-release too.

When creating the release, GitHub will save the release info and create a tag
with the provided version. The new tag will be seen by GitHub Actions, which
will then create a wheel (using the tag as version number, thanks to
`poetry-dynamic-versioning`), and push it to PyPI (using Trusted publishing).
That tag should also trigger a ReadTheDocs build, which will read GitHub
releases (thanks to our `changelog` extension) which will write the changelog
in the published documentation (transformed from `Markdown` to
`RestructuredText`).

After a new major version is released (e.g. `2.0.0`), in preparation for the next
minor release (`2.1.0`), the migration scripts in the `future_migrations` directory
that remove the SQL compatibility code must be moved to the `migrations` directory.
And the `schema.sql` file must be updated accordingly.

:::{note}
If you need to edit the name or body of a release in the GitHub UI, don't forget to
also rebuild the stable and latest doc on [readthedocs](https://readthedocs.org/projects/procrastinate/).
:::

[editorconfig]: https://editorconfig.org/
[libpq environment variables]: https://www.postgresql.org/docs/current/libpq-envars.html
[pipx]: https://pipx.pypa.io/stable/
[poetry]: https://python-poetry.org/
[pre-commit]: https://pre-commit.com/
[Procrastinate releases]: https://github.com/procrastinate-org/procrastinate/releases
[Pytest]: https://docs.pytest.org/en/latest/
