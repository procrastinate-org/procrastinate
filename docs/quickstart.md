# Quickstart

In this section, we're going to build together a small application showcasing
Procrastinate and its everyday use.

## Prerequisites & installation

If you already have a PostgreSQL database around, make sure to note the connection
parameters. Otherwise, we'll create one together with [Docker]:

```console
$ docker run --name pg-procrastinate --detach --rm -p 5432:5432 -e POSTGRES_PASSWORD=password postgres
```

:::{note}
If you need to stop the docker at some point, use `docker stop pg-procrastinate`.
:::

Within a [virtualenv], install Procrastinate with:

```console
(venv) $ pip install procrastinate
```

## Create a Procrastinate application object

We'll do this in a single file. Start an empty file named `tutorial.py`:

```
from procrastinate import App, PsycopgConnector

app = App(
    connector=PsycopgConnector(
        kwargs={
            "host": "localhost",
            "user": "postgres",
            "password": "password",
        }
    )
)
```

The application will be the entry point for both:

- Declaring tasks (a.k.a job templates) to be launched by Procrastinate,
- Launching the worker that will consume the jobs created from those tasks.
- Applying Database schema

## Prepare the database

Install the PostgreSQL structure procrastinate needs in your database with:

```console
(venv) $ export PYTHONPATH=.  # required for procrastinate to find "tutorial.app"
(venv) $ procrastinate --app=tutorial.app schema --apply
```

:::{note}
The `export PYTHONPATH=.` above is required here for the `procrastinate`
command to be able to find your `tutorial` module, and the `app` object
inside it. You wouldn't need to export `PYTHONPATH` if the `tutorial`
module was installed in the (virtual) Python environment.
:::

Are we good to go?

```console
(venv) $ procrastinate --app=tutorial.app healthchecks
App configuration: OK
DB connection: OK
Found procrastinate_jobs table: OK
```

## Declare a task

In your file, add the following

```python
# at the top of the file
import random
import time

...

# at the bottom of the file
@app.task(name="sum")
def sum(a, b):
    time.sleep(random.random() * 5)  # Sleep up to 5 seconds
    return a + b
```

We've defined a task named "sum" that will wait a bit and compute the sum of two things.
(We could have added type annotations if we wanted).

At this point, nothing is running yet. We've just created a task, which is the template
(or blueprint) for a job.

Our task doesn't really have an impact on the world (a side effect). It doesn't write a
file, or update a database, it doesn't make an API call. In real life, this is a
problem, because at this point, all the job is doing is wasting CPU cycle. In our case,
though, we'll just monitor the standard output to see if our task executed successfully.
The return value of a task serves no other purpose than logging.

## Launch a job

We'll use the `defer` method of our task

```python
import sys

...

def main():
    with app.open():
        a = int(sys.argv[1])
        b = int(sys.argv[2])
        print(f"Scheduling computation of {a} + {b}")
        sum.defer(a=a, b=b)  # This is the line that launches a job

if __name__ == "__main__":
    main()
```

You can launch your script now with:

```console
(venv) $ python tutorial.py 2 3

App is instantiated in the main Python module (tutorial.py). See https://procrastinate.readthedocs.io/en/stable/discussions.html#top-level-app
Scheduling computation of 2 + 3
```

:::{note}
We can see that Procrastinate is complaining about the fact that we're instantiating
the app in the main module (`tutorial.py`, the module on which we called Python on).
This is not a problem for this tutorial, but it's defintely something you should
avoid when building your real application. Follow the link in the warning to learn
more, but you don't need to worry about it for now.
:::

We've deferred a job, hurrah! But nothing happened yet. We need to launch a worker to
consume the job. Before that, let's defer a handful of jobs, so that we can see the
worker in action:

```console
(venv) $ python tutorial.py 5 7
(venv) $ python tutorial.py 3 9
(venv) $ python tutorial.py 1 2
```

Time to launch a worker and see what happens.

## Run a worker

```console
(venv) $ procrastinate --verbose --app=tutorial.app worker
Launching a worker on all queues
INFO:procrastinate.worker.worker:Starting worker on all queues
INFO:procrastinate.worker.worker:Starting job sum[1](a=2, b=3)
INFO:procrastinate.worker.worker:Job sum[1](a=2, b=3) ended with status: Success, lasted 1.822 s - Result: 5
```

Stop the worker with `ctrl+c`.

In the logs, you can see that the result is 5, and the task took 1.8 seconds (remember
that we added a random sleep in the task).

Congratulations, you've successfully executed your first jobs with Procrastinate!

## Checking your jobs

Procrastinate comes with a simple interactive shell to check the status of your jobs:

```console
(venv) $ procrastinate --app=tutorial.app shell
Welcome to the procrastinate shell.   Type help or ? to list commands.

procrastinate> help

Documented commands (type help <topic>):
========================================
EOF  cancel  exit  help  list_jobs  list_queues  list_tasks  retry

procrastinate> list_jobs
#1 sum on default - [succeeded]
procrastinate> exit
```

## Your final file

```python
import random
import sys
import time

from procrastinate import App, PsycopgConnector

app = App(
    connector=PsycopgConnector(
        kwargs={
            "host": "localhost",
            "user": "postgres",
            "password": "password",
        }
    )
)


@app.task(name="sum")
def sum(a, b):
    time.sleep(random.random() * 5)  # Sleep up to 5 seconds
    return a + b


def main():
    with app.open():
        a = int(sys.argv[1])
        b = int(sys.argv[2])
        print(f"Scheduling computation of {a} + {b}")
        sum.defer(a=a, b=b)  # This is the line that launches a job


if __name__ == "__main__":
    main()
```

## Going further

To continue with practical steps, head to the "{any}`howto_index`" section. For
example, have a look at the locks feature: {any}`howto/locks`.

If you want to better understand some design decisions, head to the {any}`Discussions
<discussions>` sections.

[docker]: https://docs.docker.com/
[virtualenv]: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments
