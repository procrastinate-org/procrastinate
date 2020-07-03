Glossary
========

Procrastinate uses several words with a specific meaning in the documentation and
reference materials, as well as in the user code and its own code.

Let's go through a few words and their meaning.

.. glossary::

    Task
        A task is a function executed at a later time by another process. It is linked
        to a default queue, and expects keyword arguments (see `howto/tasks`).

    Job
        A job is the launching of a specific task with specific values for the
        keyword arguments. In your code, you're mainly interacting with jobs at
        2 points: when you defer them, and when their associated
        task is executed using the job's argument values.
        The analogy would be that a job is an instance of a task.

        Using this wording, you could say, for example: "there are 2 tasks: washing the
        dishes and doing the laundry. If you did the laundry once and the dishes twice
        today, you did 3 jobs."

    Defer
        The action of instantiating a task and registering it for later execution by a
        worker.

    Queue
        This is the metaphorical place where jobs await their execution by workers.
        Each worker processes tasks from one or several queues.

    Worker
        A process responsible for processing one or more queues: taking tasks one
        by one and executing them, and then wait for the queue to fill again.

    Sub-worker
        In case of asynchronous concurrency (see `howto/concurrency`), there are
        sub-workers, acting like the :term:`Worker`, except there are multiple of them.
        They are orchestrated by the worker itself.

    App
    Application
        This is meant to be the main entry point of Procrastinate. The app knows
        all the tasks of your project, and thanks to the job store, it knows how
        to launch jobs to execute your tasks (see `App`).

    Job Store
        The job store responsibility is to store and retrieve jobs. In Procrastinate, the
        job store will store your jobs in your PostgreSQL database.

    Schema
        The schema designates all the tables, relations, indexes, procedures, etc. in the
        database. Applying the schema means installing all those objects in the database.
        An evolution in the schema (modifying the table structure, or the procedures) is
        called a migration.

        This term is not to be confused with that of PostgreSQL. In PostgreSQL a database
        contains one or more *schemas*, which in turn contains tables. Schemas in PostgreSQL
        are namespaces for objects of the database. See the `PostgreSQL Schema
        documentation`_ for more detail.

    Lock
        When configuring a job using `Task.configure` you can attach a lock to the job.
        Jobs with the same lock are guaranteed to be executed in defer order, and in a
        sequential manner. No two jobs with the same lock can run simultaneously. See
        `howto/locks` for more information.

    Queueing Lock
        When configuring a job using `Task.configure` you can attach a queueing lock to
        the job. No two jobs with the same queueing lock can be waiting in the queue.

.. _PostgreSQL Schema documentation: https://www.postgresql.org/docs/current/ddl-schemas.html
