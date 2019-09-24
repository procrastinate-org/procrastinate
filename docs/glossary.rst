Glossary
========

Procrastinate uses several words with a specific meaning in the documentation and
reference materials, as well as in the user code and its own code.

Let's go through a few words and their meaning.

.. _glossary_task:

Task
    A task is a function that would be executed later. It is linked
    to a default queue, and expects keyword arguments.

.. _glossary_job:

Job
    A job is the launching of a specific task with specific values for the
    keyword arguments. In your code, you're mainly interacting with jobs at
    2 points: when you deferring them, and when their associated
    task is executed using the job's argument values.

.. _glossary_defer:

Defer
    The action of instanciating a task and registering it for later execution by a
    worker.

Using this wording, you could say, for example: "there are 2 tasks: washing the
dishes and doing the laundry. If you did the laundry once and the dishes twice
today, you did 3 jobs."

.. _glossary_queue:

Queue
    This is the metaphorical place where jobs await their execution by workers.
    Each worker processes tasks from one or several queues.

.. _glossary_worker:

Worker
    A process responsible for processing one or more queues: taking tasks one
    by one and executing them, and then wait for the queue to fill again.

.. _glossary_app:

App (or Application) (see :py:class:`procrastinate.App`)
    This is meant to be the main entrypoint of Procrastinate. The app knows
    all the tasks of your project, and thanks to the job store, it knows how
    to launch jobs to execute your tasks.

.. _glossary_job_store:

Job Store
    The job store responsibility is to store and retrieve jobs. In Procrastinate, the
    job store will store your jobs in your PostgreSQL database.
