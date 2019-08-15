# procrastinate

Kind of like Celery but based on elephants (Postgres) instead of rabbits (RabbitMQ)

Currently very alpha stage.

## Database creation

Launch a postgres DB the way you want, e.g. using docker:

```console
$ docker-compose up -d
$ export PGDATABASE=procrastinate PGHOST=localhost PGUSER=postgres
$ createdb && psql -v ON_ERROR_STOP=ON -f init.sql
```

## Installation for development

procrastinate officially is compatible with *``Python 3.6``* and above, using Postgres 10.

```console
$ pip install -r requirements.txt
```

You may need to install some required packages for psycopg:

```console
$ apt install libpq-dev python-dev
```

## Testing

With a running database, in the dev virtualenv:

```console
$ pytest
```

## Code cleaning

In the dev virtualenv, before commiting:

```console
$ black .
$ pylint .
$ isort
```

## Demo usage

With a running database, in the dev virtualenv:

### Launch a worker

```console
$ python -m procrastinate_demo worker sums
$ python -m procrastinate_demo worker products
```

### Schedule some tasks

```console
$ python -m procrastinate_demo client
```
