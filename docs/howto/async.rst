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

    # Tasks being async or not can be awaited asynchronously or not
    await my_task.defer_async(a=1, b=2)
    # or
    my_task.defer(a=1, b=2)

As of today, jobs are still executed
sequentially, so if you have 100 asynchronous jobs that each take 1 second doing
asynchronous I/O, you would expect the complete queue to run in little over 1 second,
and instead it will take 100 seconds.

In the future, you will be able to process asynchronous jobs in parallel (see ticket__).

__ https://github.com/peopledoc/procrastinate/issues/106
