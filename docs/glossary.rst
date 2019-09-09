Glossary
========

Procrastinate uses several words with a specific meaning in the documentation and
reference materials, as well as in the user code and its own code.

Let's go through a few words and their meaning.

Asynchronous
    In Procrastinate, most of the time asynchronicity is mentioned, it's not about
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

App (or Application) (see :py:class:`procrastinate.App`)
    This is meant to be the main entrypoint of Procrastinate. The app knows
    all the tasks of your project, and thanks to the job store, it knows how
    to launch jobs to execute your tasks.

Job Store
    The job store responsibility is to store and retrieve jobs. In Procrastinate, the
    job store will store your jobs in your PostgreSQL database.
