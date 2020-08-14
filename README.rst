Procrastinate: PostgreSQL-based Task Queue for Python
=====================================================

.. image:: https://badge.fury.io/py/procrastinate.svg
    :target: https://pypi.org/pypi/procrastinate
    :alt: Deployed to PyPI

.. image:: https://readthedocs.org/projects/procrastinate/badge/?version=latest
    :target: http://procrastinate.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://github.com/peopledoc/procrastinate/workflows/CI/badge.svg?branch=master
    :target: https://github.com/peopledoc/procrastinate/actions?workflow=CI
    :alt: Continuous Integration Status

.. image:: https://codecov.io/gh/peopledoc/procrastinate/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/peopledoc/procrastinate
    :alt: Coverage Status

.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :target: https://github.com/peopledoc/procrastinate/blob/master/LICENSE
    :alt: MIT License

.. image:: https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg
    :target: CODE_OF_CONDUCT.md
    :alt: Contributor Covenant


Procrastinate is an open-source Python 3.6+ distributed task processing
library, leveraging PostgreSQL to store task definitions, manage locks and
dispatch tasks. It can be used within both sync and async code.

In other words, from your main code, you call specific functions (tasks) in a
special way and instead of being run on the spot, they're scheduled to
be run elsewhere, now or in the future.

Here's an example

.. code-block:: python

    # mycode.py

    # Make an app in your code
    app = procrastinate.App(connector=procrastinate.AiopgConnector())

    # Open the connection to the database
    app.open()

    # Then define tasks
    @app.task(queue="sums")
    def sum(a, b):
        with open("myfile", "w") as f:
            f.write(str(a + b))

    # Launch a job
    sum.defer(a=3, b=5)

    # Somewhere in your program, run a worker
    worker = procrastinate.Worker(
        app=app,
        queues=["sums"]
    )
    worker.run()

The worker will run the job, which will create a text file
named ``myfile`` with the result of the sum ``3 + 5`` (that's ``8``).

Similarly, from the command line:

.. code-block:: bash

    export PROCRASTINATE_APP="mycode.app"

    # Launch a job
    procrastinate defer mycode.sum '{"a": 3, "b": 5}'

    # Run a worker
    procrastinate worker sums

Lastly, you can use Procrastinate asynchronously too:

.. code-block:: python

    # Define asynchronous tasks using coroutine functions
    @app.task(queue="sums")
    async def sum(a, b):
        await asyncio.sleep(a + b)

    # Launch a job asynchronously
    await sum.defer_async(a=3, b=5)

    # Somewhere in your program, run a worker asynchronously
    worker = procrastinate.Worker(
        app=app,
        queues=["sums"]
    )
    await worker.run_async()

There are quite a few interesting features that Procrastinate adds to the mix.
You can head to the Quickstart section for a general tour or
to the How-To sections for specific features. The Discussion
section should hopefully answer your questions. Otherwise,
feel free to open an `issue <https://github.com/peopledoc/procrastinate/issues>`_.

The project is still quite early-stage and will probably evolve.

*Note to my future self: add a quick note here on why this project is named*
"Procrastinate_".

.. _Procrastinate: https://en.wikipedia.org/wiki/Procrastination

.. Below this line is content specific to the README that will not appear in the doc.
.. end-of-index-doc

Where to go from here
---------------------

The complete docs_ is probably the best place to learn about the project.

If you encounter a bug, or want to get in touch, you're always welcome to open a
ticket_.

.. _docs: http://procrastinate.readthedocs.io/en/latest
.. _ticket: https://github.com/peopledoc/procrastinate/issues/new
