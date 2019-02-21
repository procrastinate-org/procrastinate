# Cabbage

Kind of like Celery but based on elephants (Postgres) instead of rabbits (RabbitMQ)

Currently very alpha stage.

## Database creation

Launch a postgres DB the way you want, e.g. using docker:

```console
$ docker run --rm -it -p 5432:5432 postgres
$ export PGDATABASE=cabbage PGHOST=localhost PGUSER=postgres
$ createdb && psql -v ON_ERROR_STOP=ON -f init.sql
```

## Installation for development
```console
$ pip install -r requirements.txt
```

## Testing

With a running database, in the dev virtualenv:

```console
$ pytest
```

## Demo usage

With a running database, in the dev virtualenv:

### Launch a worker

```console
$ python -m cabbage_demo worker sums
$ python -m cabbage_demo worker products
```

### Schedule some tasks

```console
$ python -m cabbage_demo client
```


