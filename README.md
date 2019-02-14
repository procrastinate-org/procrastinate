# Cabbage

Kind of like Celery but based on elephants (Postgres) instead of rabbits (RabbitMQ)

Currently very alpha stage.

## Database

Launch a postgres DB the way you want, e.g. using docker:

```console
$ docker run --rm -it -p 5432:5432 postgres
$ export PGDATABASE=cabbage PGHOST=localhost PGUSER=postgres
$ createdb && psql -f migration.sql
```

## Launch a worker

```console
$ python -m cabbage worker
```


## Schedule some tasks

```console
$ python -m cabbage client
```
