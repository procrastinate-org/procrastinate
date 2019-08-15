Discussions
===========

Why are you doing a task queue in Postgres ?
--------------------------------------------

Because while maintaining a large Postgres_ database in good shape in
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

.. _Postgres: https://www.postgresql.org/
.. _RabbitMQ: https://www.rabbitmq.com/
.. _Redis: https://redis.io/

There are 14 standards...
-------------------------

.. figure:: https://imgs.xkcd.com/comics/standards.png
    :alt: https://xkcd.com/927/

    https://xkcd.com/927/

We are aware that Procrastinate is an addition to an already crowded market of
Python task queues, and the aim is not to replace them all, but to provide
an alternative that fits our need, where we could not find one we were
completely satifified with.

Nethertheless, we acknowledge the impressive Open Source work accomplished by
some projects that really stand out, to name a few:

- Celery_: Is really big and supports a whole variety of cases, but not using
  ``postgres`` as a message queue. We could have tried to add this, but it
  really feels like Celery is doing a lot already, and every addition to it is
  a lot of compromises, and would probably have been a lot harder.
- Dramatiq_ + dramatiq-pg_: Dramatiq is another very nice Python task queue
  that does things quite well, and it happens that there is a third party
  addition for using postgres as a backend. In fact, it was built around the
  same time as we started Procrastinate, and the paradigm it uses makes it hard to
  integrate a few of the feature we really wanted to use Procrastinate for, namely
  locks.


.. _Celery: https://docs.celeryproject.org
.. _Dramatiq: https://dramatiq.io/
.. _dramatiq-pg: https://pypi.org/project/dramatiq-pg/


How stable is Procrastinate ?
-----------------------------

Not quite stable. There a lot of things we would like to do before we start
advertising the project, and so far, it's not used anywhere.

We'd love if you were to try out Procrastinate in a non-production non-critical
project of yours and provide us with feedback.

Glossary
--------

Procrastinate uses several words with a specific meaning in the documentation and
reference materials, as well as in the user code and it's own code.

Let's lay down a few words their meaning.

Asynchronous
    In Procrastinate, most of the time asynchronoucity is metionned, it's not about
    Python's ``async/await`` features, but about the fact a job is launched
    in the code, and then the calling code moves on, not waiting for the
    completion of the job. Because of this, asynchronous tasks should have a
    side effect, and do something that modifies the world (e.g. compute a costly
    function **and** store the result somewhere), otherwise the result of the
    computation will be lost.

Task
    A task is a function that would be executed asynchronously. It is linked
    to a default queue, and expects keyword arguments.

Job
    A job is the launching of a specific task with specific values for the
    keyword arguments. In your code, you're mainly interacting with jobs at
    2 points: when you launch them asynchronously, and when their associated
    task is executed using the job's argument values.

Using this wording, you could say, for example: "there are 2 tasks: washing the
dishes and doing the laundry. If you did the laundry once and the dishes twice
today, you did 3 jobs."

Queue
    This is the metaphorical place where jobs await their execution by workers.
    Each worker processes tasks from one or several queues.

Worker
    A process responsible for processing one or more queues: taking tasks one
    by one and executing them, and then wait for the queue to fill again.

App
    This is meant to be the main entrypoint of Procrastinate. The app knows
    all the tasks of your project, and thanks to the job store, it knows how
    to launch jobs to execute your tasks.

Job Store
    The job store resposability is to store and retrieve jobs. In Procrastinate, the
    job store will store your jobs in your ``postgres`` database.

Thanks PeopleDoc
----------------

This project was almost entirely created by PeopleDoc employees on their
working time. Let's take this opportunity to thank PeopleDoc for funding
an Open Source projects like this!

If this makes you want to know more about this company, check our website_
or our `job offerings`_ !

.. _website: https://www.people-doc.com/
.. _`job offerings`: https://www.people-doc.com/company/careers
