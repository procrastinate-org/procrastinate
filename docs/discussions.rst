.. _discussions:

Discussions
===========

How does this all work ?
------------------------

Procrastinate is based on several things:

- PostgreSQL's top notch ability to manage locks, thanks to its ACID_ properties.
  This ensures that when a worker starts executing a job, it's the only one.
  Procrastinate does this by executing a ``SELECT FOR UPDATE`` that will lock the
  jobs table. This might not scale to billions of simultaneous tables, but we don't
  expect to reach that level.
- PostgreSQL's LISTEN_ allows us to be notified whenever a task is available.

.. _ACID: https://en.wikipedia.org/wiki/ACID
.. _LISTEN: https://www.postgresql.org/docs/current/sql-listen.html

Why are you doing a task queue in PostgreSQL ?
----------------------------------------------

Because while maintaining a large PostgreSQL_ database in good shape in
our infrastructure is no small feat, also maintaining a RabbitMQ_/Redis_/...
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

.. _PostgreSQL: https://www.postgresql.org/
.. _RabbitMQ: https://www.rabbitmq.com/
.. _Redis: https://redis.io/

There are 14 standards...
-------------------------

.. figure:: https://imgs.xkcd.com/comics/standards.png
    :alt: https://xkcd.com/927/

    https://xkcd.com/927/

We are aware that Procrastinate is an addition to an already crowded market of
Python task queues, and the aim is not to replace them all, but to provide
an alternative that fits our need, as we could not find one we were
completely satisfied with.

Nevertheless, we acknowledge the impressive Open Source work accomplished by
some projects that really stand out, to name a few:

- Celery_: Is really big and supports a whole variety of cases, but not using
  PostgreSQL as a message queue. We could have tried to add this, but it
  really feels like Celery is doing a lot already, and every addition to it is
  a lot of compromises, and would probably have been a lot harder.
- Dramatiq_ + dramatiq-pg_: Dramatiq is another very nice Python task queue
  that does things quite well, and it happens that there is a third party
  addition for using PostgreSQL as a backend. In fact, it was built around the
  same time as we started Procrastinate, and the paradigm it uses makes it hard to
  integrate a few of the feature we really wanted to use Procrastinate for, namely
  locks.


.. _Celery: https://docs.celeryproject.org
.. _Dramatiq: https://dramatiq.io/
.. _dramatiq-pg: https://pypi.org/project/dramatiq-pg/

.. _discussion-locks:

About locks
-----------

Let's say we have a task that writes a character at the end of a file after waiting for
a random amount of time. This represents a real world problem where tasks take an
unforeseeable amount of time and share resources like a database.

We launch 4 tasks respectively writing ``a``, ``b``, ``c`` and ``d``. We would expect
the file to contain ``abcd``, but it's not the case, for example maybe it's ``badc``.
The jobs were taken from the queue in order, but because we have several workers, the
jobs were launched in parallel and because their duration is random, the final result
pretty much is too.

We can solve this problem by using locks. Procrastinate gives us two guarantees:

- Tasks are consumed in creation order. When a worker requests a task, it will always
  receive the oldest available task. Unavailable tasks, either locked, scheduled for the
  future or in a queue that the worker doesn't listen to, will be ignored.
- If a group of tasks share the same lock, then only one can be executed at a time.

These two facts allow us to draw the following conclusion for our 4 letter tasks from
above. If our 4 tasks share the same lock (for example, the name of the file we're
writing to):

- The 4 tasks will be started in order;
- A task will not start before the previous one is finished.

This says we can safely expect the file to contain ``abcd``.

Note that Procrastinate will use PostgreSQL to search the jobs table for suitable jobs.
Even if the database contains a high proportion of locked tasks, this will barely affect
Procrastinates's capacity to quickly find the free tasks.

A good string identifier for the lock is a string identifier of the shared resource,
UUIDs are well suited for this. If multiple resources are implicated, a combination of
their identifiers could be used (there's no hard limit on the length of a lock string,
but stay reasonable).

A task can only take a single lock so there's no dead-lock scenario possible where two
running tasks are waiting one another. That being said, if a worker dies with a lock, it
will be up to you to free it. If the task fails but the worker survives though, the
lock will be freed.

For a more practical approach, see :ref:`how-to-locks`.

.. _discussion-async:

Asynchronous interface
----------------------

Here, asynchronous (or async) means "using the Python `async/await` keywords, to make
I/Os run in parallel". Asynchronous work can be tricky in Python because once you start
having something asynchronous, you soon realize everything needs to be asynchronous for
it to work.

Procrastinate aims at being compatible with both sync and async codebases.

There are two distinct parts in procrastinate that are relevant for asynchronous work:
deferring a job, and executing it. As a rule of thumb, only use asynchronous interface
when you need it.

If you have, for example, an async web application, you will need to defer jobs
asynchronously. You can't afford blocking the whole event loop while you connect to
the database and send your job.

There are mainly two use-cases where you may want to execute your jobs asynchronously.
Either they do long I/O calls that you would like to run in parallel, or you plan to
reuse parts of your codebase written with the asynchronous interface (say, an async ORM)
and you don't want to have to maintain their equivalent using a synchronous interface.

There's a catch, though. If your tasks are not async-friendly (time consuming,
either CPU intensive or they do synchronous I/O calls), you probably want to avoid
executing them asynchronously. They will probably not perform worse but it may
be disturbing for the reader, and if you ever implement tasks with real asynchronous
I/O calls, they will perform badly because your event loop will be blocked.

You can have a combination of synchronous and asynchronous tasks in your codebase, as
long as they are handled by two distinct workers (one async and one sync)

So far, the only asynchronous interface implemented in procrastinate is job deferring.

See :ref:`how-to-async` for API details.

Procrastinate's database interactions
-------------------------------------

A few things are worth noting in our PostgreSQL usage.

Using procedures
^^^^^^^^^^^^^^^^

For critical requests, we tend to using PostgreSQL procedures where we could do the same
thing directly with queries. This is so that the database is solely responsible for
consistency, and would allow us to have the same behavior if someone were to write
a procrastinate compatible client, in Python or in another language altogether.

The ``procrastinate_job_locks`` table
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We could have used PostgreSQL's `advisory locks`_, and we choose to kinda "reimplement
the wheel" with a dedicated table. This is because we made the choice that if a worker
dies holding a lock, we'd rather have a human examine the situation and manually free
the lock than having the lock been automatically freed, and fail our locks consistency
guarantee.

.. _`advisory locks`: https://www.postgresql.org/docs/10/explicit-locking.html#ADVISORY-LOCKS

So far, Procrastinate implements async job deferring, and async job executing but
not in parallel, meaning it can run jobs written as a coroutine, but it will
only execute one job at a time.

Why is Procrastinate asynchronous at core?
------------------------------------------

There are several ways to write a program that can be called from both a synchronous
and an asynchronous code:

- Duplicate the codebase. It's not a fantastic idea. There's a high probability that
  this will lead to awkward bugs, you'll have twice the work in maintenance etc.
  The good thing is that it will force you to extract as much as the logic in a common
  module, and have the I/Os very decoupled.

- Have the project be synchronous, and provide top level asynchronous wrappers that
  run the synchronous code in a thread. This can be a possibility, but then you enter
  a whole new circle of thread safety hell.

- Have the project be asynchronous, and provide top level synchronous wrappers that
  will synchronously launch coroutines in the event loop and wait for them to be
  completed. This is virtually the best solution we could find, and thus it's what
  we decided to do.

We've even cheated a bit: instead of implementing our synchronous wrappers manually,
we've been using a trick that autogenerates a synchronous API based on our asynchronous
API. This way, we have less code to unit-test, and we can guarantee that the 2 APIs
will stay synchronized in the future no matter what. Want to know more about this?
Here are a few resources:

- How we generate our sync API:
  https://github.com/peopledoc/procrastinate/blob/master/procrastinate/utils.py
- An interesting talk on the issues that appear when trying to make codebases compatible
  with sync **and** async callers: "Just add await" from Andrew Godwin:
  https://www.youtube.com/watch?v=oMHrDy62kgE

How stable is Procrastinate?
----------------------------

More and more stable. There are still a few things we would like to do before we start
advertising the project, and it's about to be used in production at our place.

We'd love if you were to try out Procrastinate in a non-production non-critical
project of yours and provide us with feedback.


Wasn't this project named "Cabbage" ?
-------------------------------------

Yes, in early development, we planned to call this "cabbage" in reference to
celery, but even if the name was available on PyPI, by the time we stopped
procrastinating and wanted to register it, it had been taken. Given this project
is all about "launching tasks in an undetermined moment in the future", the new
name felt quite adapted too. Also, now you know why the project is named this way.

Thanks PeopleDoc
----------------

This project was almost entirely created by PeopleDoc employees on their
working time. Let's take this opportunity to thank PeopleDoc for funding
an Open Source projects like this!

If this makes you want to know more about this company, check our website_
or our `job offerings`_ !

.. _website: https://www.people-doc.com/
.. _`job offerings`: https://www.people-doc.com/company/careers
