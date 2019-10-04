.. _how-to-async:

Launch a job and/or execute it asynchronously
---------------------------------------------

First, make sure you understand the implications of using the asynchronous interface
(see :ref:`discussion-async`).

In order to user the asynchronous interface, you'll need to install extra dependencies
using:

.. code-block:: console

    $ pip install 'procrastinate[async]'

Then, the :py:class:`procrastinate.App` has to be configured with an
:py:class:`procrastinate.aiopg_connector.AiopgJobStore` ``job_store``::

    import procrastinate
    from procrastinate.aiopg_connector import AiopgJobStore

    app = procrastinate.App(
        job_store=AiopgJobStore(dsn="...")
    )


Defer jobs asynchronously
^^^^^^^^^^^^^^^^^^^^^^^^^

If your job store is asynchronous, then instead of calling ``defer``, you'll need
to call ``defer_async``::

    @app.task
    def my_task(a, b):
        pass

    await my_task.defer_async(a=1, b=2)
    await my_task.configure(lock="ness").defer_async(a=1, b=2)
    await app.configure_task(name="module.my_task", lock="ness").defer_async(a=1, b=2)



Execute jobs asynchronously
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This has not been implemented yet.
