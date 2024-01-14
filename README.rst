Procrastinate: PostgreSQL-based Task Queue for Python
=====================================================


.. image:: https://img.shields.io/pypi/v/procrastinate?logo=pypi&logoColor=white
    :target: https://pypi.org/pypi/procrastinate
    :alt: Deployed to PyPI

.. image:: https://img.shields.io/pypi/pyversions/procrastinate?logo=pypi&logoColor=white
    :target: https://pypi.org/pypi/procrastinate
    :alt: Deployed to PyPI

.. image:: https://img.shields.io/github/stars/procrastinate-org/procrastinate?logo=github
    :target: https://github.com/procrastinate-org/procrastinate/
    :alt: GitHub Repository

.. image:: https://img.shields.io/github/actions/workflow/status/procrastinate-org/procrastinate/ci.yml?logo=github&branch=main
    :target: https://github.com/procrastinate-org/procrastinate/actions?workflow=CI
    :alt: Continuous Integration

.. image:: https://img.shields.io/readthedocs/procrastinate/stable?logo=read-the-docs&logoColor=white
    :target: https://procrastinate.readthedocs.io/en/stable/badge=stable
    :alt: Documentation

.. image:: https://img.shields.io/endpoint?logo=codecov&logoColor=white&url=https://raw.githubusercontent.com/wiki/procrastinate-org/procrastinate/python-coverage-comment-action-badge.json
    :target: https://github.com/marketplace/actions/python-coverage-comment
    :alt: Coverage

.. image:: https://img.shields.io/github/license/procrastinate-org/procrastinate?logo=open-source-initiative&logoColor=white
    :target: https://github.com/procrastinate-org/procrastinate/blob/main/LICENSE
    :alt: MIT License

.. image:: https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg
    :target: https://github.com/procrastinate-org/procrastinate/blob/main/CODE_OF_CONDUCT.md
    :alt: Contributor Covenant

**Procrastinate is looking for** `additional maintainers! <https://github.com/procrastinate-org/procrastinate/discussions/748>`_

Procrastinate is an open-source Python 3.8+ distributed task processing
library, leveraging PostgreSQL to store task definitions, manage locks and
dispatch tasks. It can be used within both sync and async code and integrated
to Django.

In other words, from your main code, you call specific functions (tasks) in a
special way and instead of being run on the spot, they're scheduled to
be run elsewhere, now or in the future.

Here's an example (if you want to run the code yourself, head to Quickstart_):

.. code-block:: python

    # mycode.py
    import procrastinate

    # Make an app in your code
    app = procrastinate.App(connector=procrastinate.SyncPsycopgConnector())

    # Then define tasks
    @app.task(queue="sums")
    def sum(a, b):
        with open("myfile", "w") as f:
            f.write(str(a + b))

    with app.open():
        # Launch a job
        sum.defer(a=3, b=5)

    # Somewhere in your program, run a worker (actually, it's usually a
    # different program than the one deferring jobs for execution)
    app.run_worker(queues=["sums"])

The worker will run the job, which will create a text file
named ``myfile`` with the result of the sum ``3 + 5`` (that's ``8``).

Similarly, from the command line:

.. code-block:: bash

    export PROCRASTINATE_APP="mycode.app"

    # Launch a job
    procrastinate defer mycode.sum '{"a": 3, "b": 5}'

    # Run a worker
    procrastinate worker -q sums

Lastly, you can use Procrastinate asynchronously too (actually, it's the
recommended way to use it):

.. code-block:: python

    import asyncio

    import procrastinate

    # Make an app in your code
    app = procrastinate.App(connector=procrastinate.PsycopgConnector())

    # Define tasks using coroutine functions
    @app.task(queue="sums")
    async def sum(a, b):
        await asyncio.sleep(a + b)

    async with app.open_async():
        # Launch a job
        await sum.defer_async(a=3, b=5)

        # Somewhere in your program, run a worker (actually, it's often a
        # different program than the one deferring jobs for execution)
        await app.run_worker_async(queues=["sums"])

There are quite a few interesting features that Procrastinate adds to the mix.
You can head to the Quickstart section for a general tour or
to the How-To sections for specific features. The Discussion
section should hopefully answer your questions. Otherwise,
feel free to open an `issue <https://github.com/procrastinate-org/procrastinate/issues>`_.

*Note to my future self: add a quick note here on why this project is named*
"Procrastinate_" ;) .

.. _Procrastinate: https://en.wikipedia.org/wiki/Procrastination
.. _Quickstart: https://procrastinate.readthedocs.io/en/stable/quickstart.html

.. Below this line is content specific to the README that will not appear in the doc.
.. end-of-index-doc

Where to go from here
---------------------

The complete docs_ is probably the best place to learn about the project.

If you encounter a bug, or want to get in touch, you're always welcome to open a
ticket_.

.. _docs: https://procrastinate.readthedocs.io/
.. _ticket: https://github.com/procrastinate-org/procrastinate/issues/new
