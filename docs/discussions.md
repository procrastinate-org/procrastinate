# Discussions

(discussion-general)=

## How does this all work ?

Procrastinate is based on several things:

- PostgreSQL's top notch ability to manage locks, thanks to its [ACID] properties.
  This ensures that when a worker starts executing a {term}`job`, it's the only one.
  Procrastinate does this by executing a `SELECT FOR UPDATE` that will lock the
  impacted rows, and ensure no other process can edit the same row.
- PostgreSQL's [LISTEN] allows us to be notified whenever a task is available.

## Why are you doing a task queue in PostgreSQL ?

Because while maintaining a large [PostgreSQL] database in good shape in
our infrastructure is no small feat, also maintaining a [RabbitMQ]/[Redis]/...
service is double the trouble. It introduces plenty of problems around backups,
high availability, monitoring, etc. If you already have a stable robust
database, and this database gives you all the tooling you need to build
a message queue on top of it, then it's always an option you have.

Another nice thing is the ability to easily browse (and possibly edit) jobs in
the queue, because interacting with data in a standard database a lot easier
than implementing a new specific protocol (say, AMQP).

This makes the building of tools around Procrastinate quite easier.

Finally, the idea that the core operations around tasks are handled by the
database itself using stored procedures eases the possibility of porting
Procrastinate to another language, while staying compatible with Python-based jobs.

## There are 14 standards...

:::{figure} https://imgs.xkcd.com/comics/standards.png
:alt: https://xkcd.com/927/

<https://xkcd.com/927/>
:::

We are aware that Procrastinate is an addition to an already crowded market of
Python task queues, and the aim is not to replace them all, but to provide
an alternative that fits our need, as we could not find one we were
completely satisfied with.

Nevertheless, we acknowledge the impressive Open Source work accomplished by
some projects that really stand out, to name a few:

- [Celery]: Is really big and supports a whole variety of cases, but not using
  PostgreSQL as a message queue. We could have tried to add this, but it
  really feels like Celery is doing a lot already, and every addition to it is
  a lot of compromises, and would probably have been a lot harder.
- [Dramatiq] + [dramatiq-pg]: Dramatiq is another very nice Python task queue
  that does things quite well, and it happens that there is a third party
  addition for using PostgreSQL as a backend. In fact, it was built around the
  same time as we started Procrastinate, and the paradigm it uses makes it hard to
  integrate a few of the feature we really wanted to use Procrastinate for, namely
  locks.

(top-level-app)=

## Defining your app at the top level of your program

It can be tempting to define your procrastinate app at the top level of your
application, and in many cases, this will be the perfect place, but you need
to be aware of several caveats:

- Your app needs to know about your tasks. This either means that all the tasks
  must be defined in the same module as the app, or that you need to correctly
  submit the `import_paths` argument of <project:#procrastinate.App> to point to all the modules
  that define a task (or that importing the module containing your app should,
  as a side effect, import all modules containing all of your tasks, but that
  last possibility is more error-prone).
- If your procrastinate app is defined in the module (let's call it
  `that_module.py`) in which `__name__ == "__main__"` (which means you
  launch your program with either `python that_module.py` or `python -m
  that_module`), AND if your tasks are defined in a different module which
  does `import that_module`, then you will end up with two distinct instances
  of your app (`__main__.app` and `that_module.app`) and you will likely
  run into problems. The best thing to do in this case is to create a dedicated
  module for your app (e.g. `procrastinate.py`) (or to put everything in the
  same module, but this doesn't scale well).

(discussion-locks)=

## About locks

Let's say we have a {term}`task` that writes a character at the end of a file after
waiting for a random amount of time. This represents a real world problem where jobs
take an unforeseeable amount of time and share resources like a database.

We launch 4 jobs respectively writing `a`, `b`, `c` and `d`. We would expect
the file to contain `abcd`, but it's not the case, for example maybe it's `badc`.
The jobs were taken from the queue in order, but because we have several workers, the
jobs were launched in parallel and because their duration is random, the final result
pretty much is too.

We can solve this problem by using locks. Procrastinate gives us two guarantees:

- Jobs are consumed in priority and creation order. When a worker requests a job, it can receive
  a job with a lock, or a job without a lock. If there is a lock, then the received
  job will be the highest priority, oldest (in that order) one with that lock. If that job awaiting execution is
  not available for this worker (either it's on a queue that this worker doesn't
  listen to, or it's scheduled in the future), then jobs with this lock will not be
  considered.
- If a group of jobs share the same lock, then only one can be executed at a time.

These two facts allow us to draw the following conclusion for our 4 letter jobs from
above. If our 4 jobs share the same lock (for example, the name of the file we're
writing to):

- The 4 jobs will be started in order;
- A job will not start before the previous one is finished.

This says we can safely expect the file to contain `abcd`.

Note that Procrastinate will use PostgreSQL to search the jobs table for suitable jobs.
Even if the database contains a high proportion of locked jobs, this will barely affect
Procrastinate's capacity to quickly find the free jobs.

A good string identifier for the lock is a string identifier of the shared resource,
UUIDs are well suited for this. If multiple resources are implicated, a combination of
their identifiers could be used (there's no hard limit on the length of a lock string,
but stay reasonable).

A job can only take a single lock so there's no dead-lock scenario possible where two
running jobs are waiting for one another. If a worker is killed without ending its job,
following jobs with the same lock will not run until the interrupted job is either
manually set to "failed" or "succeeded". If a job simply fails, following jobs with the
same locks may run.

For a more practical approach, see {doc}`howto/advanced/locks`.

(discussion-async)=

## What are the different states of a Job and how do they go from one to another?

A job can be in one of the following states:

```{mermaid}
flowchart LR
    START:::hidden
    todo[TODO]
    doing[DOING]
    succeeded[SUCCEEDED]
    failed[FAILED]
    cancelled[CANCELLED]
    aborted[ABORTED]
    START -- a --> todo
    todo -- b --> doing
    doing -- c --> succeeded
    doing -- d --> todo
    doing -- e --> failed
    todo -- f --> cancelled
    doing -- g --> aborted
    classDef hidden display: none;
```

- **a**: The job was deferred by `my_task.defer()` (or the async equivalent)
- **b**: A worker fetched the job from the database and started processing it
- **c**: A worker finished processing a job successfully
- **d**: The job failed by raising an error but will be retried
- **e**: The job failed by raising an error and won't be retried
- **f**: The job was cancelled by calling `job_manager.cancel_job_by_id(job_id)` (or the async equivalent) before its processing was started
- **g**: The job was aborted during being processed by calling
  `job_manager.cancel_job_by_id(job_id, abort=True)` (or the async equivalent). A sync job must also
  handle the abort request by checking `context.should_abort()` and raising a
  `JobAborted` exception. An async job handles it automatically by internally raising a
  `CancelledError` exception.

## Asynchronous operations & concurrency

Here, asynchronous (or async) means "using the Python `async/await` keywords, to
make I/Os run in parallel". Asynchronous work can be tricky in Python because once you
start having something asynchronous, you soon realize everything needs to be
asynchronous for it to work.

Procrastinate aims at being made for async codebases and tries its best to offer
compatibility with synchronous codebases too. Because of this, you will always need
to set up an asynchronous connector for running the worker, or the procrastinate CLI.

There are three distinct parts in procrastinate that are relevant for asynchronous work:
{term}`deferring <Defer>` a {term}`job`, executing it in the worker, and introspecting
Procrastinate to get information about the jobs.

If you have, for example, an synchronous web application (e.g. using Django or
Flask), you will want to defer jobs synchronously. Procrastinate supports a
synchronous {py:meth}`Task.defer` function (see {ref}`sync-defer`).

:::{note}
When you define an asynchronous connector, Procrastinate will try to
seamlessly give you the right connector for your context. When you call
the synchronous API, it will either create a sync connector based on your
async connector, or let you use the async connector directly with
`asgiref.sync.async_to_sync`.
:::

For running jobs, support of synchronous task functions is through
`asgiref.sync.sync_to_async`. This means your synchronous function will be
executed by an asynchronous worker in a thread. Because of the [Global
Interpreter Lock][global interpreter lock], you will not benefit from parallelism, but you will still be able
to parallelize (thread-safe) I/Os.

Procrastinate natively supports asynchronous job deferring, and asynchronous job
execution (see {doc}`howto/production/concurrency`, {doc}`howto/advanced/sync_defer`).

(discussions-pool-size)=

### Mind the size of your PostgreSQL pool

You can size the PostgreSQL pool using the `max_size` argument of
{py:class}`PsycopgConnector`. Procrastinate will use one connection to listen to
server-side `NOTIFY` calls (see {ref}`discussion-general`). That connection
is not counted in the pool which is only is used for {term}`sub-workers
<Sub-worker>`.

:::{warning}
In previous versions of Procrastinate, setting `max_size` to `1`:
disabled `LISTEN/NOTIFY`. It's not the case anymore. Note that disabling
this feature is possible with `listen_notify=False`, see
{doc}`howto/production/connections`.
:::

The relative sizing of your pool and your sub-workers all depends on the average length
of your jobs, and especially compared to the time it takes to fetch jobs and register
job completion.

The shorter your average job execution time, the more your pool will need to contain as
many connections as your concurrency (plus one). And vice versa: the longer your job
time, the smaller your pool may be.

Having sub-workers wait for an available connection in the pool is suboptimal. Your
resources will be better used with fewer sub-workers or a larger pool, but there are
many factors to take into account when [sizing your pool](https://wiki.postgresql.org/wiki/Number_Of_Database_Connections).

### How polling works

#### `fetch_job_polling_interval`

Even when the database doesn't notify workers regarding newly deferred jobs, each worker still poll the database every now and then, just in case.
There could be previously locked jobs that are now free, or scheduled jobs that have
reached the ETA. `fetch_job_polling_interval` is the {py:meth}`App.run_worker` parameter (or the
equivalent CLI flag) that sizes this "every now and then".

A worker will keep fetching new jobs as long as they have capacity to process them.
The polling interval starts from the moment the last attempt to fetch a new job yields no result.

:::{note}
The polling interval was previously called `timeout` in pre-v3 versions of Procrastinate. It was renamed to `fetch_job_polling_interval` for clarity.
:::

#### `abort_job_polling_interval`

Another polling interval is the `abort_job_polling_interval`. It defines how often the worker will poll the database for jobs to abort.
When `listen_notify=True`, the worker will likely be notified "instantly" of each abort request prior to polling the database.

However, when `listen_notify=False` or the abort notification was missed, `abort_job_polling_interval` will represent the maximum delay before the worker reacts to an abort request.

Note that the worker will only poll the database for abort requests when at least one job is running.

## Procrastinate's usage of PostgreSQL functions and procedures

For critical requests, we tend to using PostgreSQL procedures where we could do the same
thing directly with queries. This is so that the database is solely responsible for
consistency, and would allow us to have the same behavior if someone were to write
a procrastinate compatible client, in Python or in another language altogether.

## Why is Procrastinate asynchronous at core?

It's quite hard for a single library to be both synchronous and asynchronous.
The problem is that the user code may be synchronous or asynchronous, and will
call the library, but the library needs to be able to call the user code too.

In procrastinate, the user code calling the library is what happens when you
defer a job. The library calling the user code is what happens when a job is
executed in the worker.

The issue is always when switching between synchronous and asynchronous code.
By choosing to make Procrastinate asynchronous, we make it easy to integrate
with asynchronous codebases, but it's harder to integrate with synchronous
codebases.

Here are the tricks we're using to make synchronous codebases work with
Procrastinate:

- For synchronously deferring a task: we duplicate a small part of the code. We have a
  synchronous version of the code that uses a synchronous database driver, and
  an asynchronous version of the code that uses an asynchronous database
  driver. Under the hood, we have factored as much as possible the non-I/O
  parts of the code, so that the synchronous and asynchronous versions are
  only separate in the way they handle I/Os.
- For executing a synchronous task: we use `asgiref.sync.sync_to_async` to run the
  synchronous code in a thread.
- There are a few case where we facilitate calling Procrastinate from
  synchronous codebases, by providing a synchronous API, where we'll create an
  event loop and execute the corresponding asynchronous code in it. This is the
  case for {py:meth}`App.run_worker`. It's ok for a long-lived call like this one, but
  it would not be recommended to do that for short-lived calls.

## How stable is Procrastinate?

Quite stable in that it hasn't been moving a lot in the past few years, and has been
used in production for small systems for years. In 2023, we started trying to improve
the sync/async story, and this is still a work in progress.

That being said, we'd like to develop real monitoring tools before we call this
really ready for production.

We'd love if you were to try out Procrastinate in a project of yours and
provide us with feedback.

## Does Procrastinate provide any benchmarks?

We run some very [basic benchmarks](https://github.com/procrastinate-org/procrastinate/tree/main/tests/benchmarks)
on every commit of the main branch to detect performance regressions.
The visualized results can be viewed on our [Benchmarks GitHub Page](https://procrastinate-org.github.io/procrastinate/dev/bench/).

## Wasn't this project named "Cabbage" ?

Yes, in early development, we planned to call this "cabbage" in reference to
celery, but even if the name was available on PyPI, by the time we stopped
procrastinating and wanted to register it, it had been taken. Given this project
is all about "launching jobs in an undetermined moment in the future", the new
name felt quite adapted too. Also, now you know why the project is named this way.

(peopledoc)=

## Thanks PeopleDoc / UKG

This project was largely created by PeopleDoc employees on their
working time. Let's take this opportunity to thank PeopleDoc for funding
[Open Source projects](https://github.com/peopledoc/) like this!

[acid]: https://en.wikipedia.org/wiki/ACID
[celery]: https://docs.celeryproject.org
[dramatiq]: https://dramatiq.io/
[dramatiq-pg]: https://pypi.org/project/dramatiq-pg/
[global interpreter lock]: https://docs.python.org/3/glossary.html#term-global-interpreter-lock
[listen]: https://www.postgresql.org/docs/current/sql-listen.html
[postgresql]: https://www.postgresql.org/
[rabbitmq]: https://www.rabbitmq.com/
[redis]: https://redis.io/
