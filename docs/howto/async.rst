Launch a job and/or execute it asynchronously
---------------------------------------------

First, make sure you understand the implications of using the asynchronous interface
(see `discussion-async`).

Defer jobs asynchronously
^^^^^^^^^^^^^^^^^^^^^^^^^

In order for the defer query to be executed asynchronously, instead of calling
``defer``, you'll need to call ``defer_async``::

    @app.task
    def my_task(a, b):
        pass

    await my_task.defer_async(a=1, b=2)
    await my_task.configure(lock="ness").defer_async(a=1, b=2)
    await app.configure_task(name="module.my_task", lock="ness").defer_async(a=1, b=2)



Execute jobs asynchronously
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your job is a coroutine, it will be awaited::

    @app.task
    async def my_task(a, b):
        await asyncio.sleep(3)

With async tasks (such as ``my_task`` above), and with ``concurrency`` set to a value
greater than ``1`` in the Procrastinate worker, the worker process may execute multiple
jobs at the same time. See `./concurrency` for more information on how to configure
Procrastinate workers for concurrent jobs.

Note that tasks can be deferred asynchronously or synchronously, whether they are async
or not::

    # Note: tasks being async or not can be awaited asynchronously or not
    await my_task.defer_async(a=1, b=2)
    # or
    my_task.defer(a=1, b=2)
