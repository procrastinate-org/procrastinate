Procrastinate: PostgreSQL-based Task Queue for Python
=====================================================

.. image:: https://badge.fury.io/py/procrastinate.svg
    :target: https://pypi.org/pypi/procrastinate
    :alt: Deployed to PyPI

.. image:: https://readthedocs.org/projects/procrastinate/badge/?version=latest
    :target: http://procrastinate.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/peopledoc/procrastinate.svg?branch=master
    :target: https://travis-ci.org/peopledoc/procrastinate
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
dispatch tasks.

In other words, from your main code, you schedule jobs (a.k.a. function calls)
and a dedicated worker process will execute all the enqueued jobs immediately or
later.

Here's an example

.. code-block:: python

    # Make a app in your code
    app = procrastinate.App(job_store=procrastinate.PostgresJobStore())

    # Then define tasks
    @app.task(queue="sums")
    def sum(a, b):
        with open("myfile", "w") as f:
            f.write(str(a + b))

    # Launch tasks
    sum.defer(a=3, b=5)

    # Somewhere in your program, launch a worker
    worker = procrastinate.Worker(
        app=app,
        queues=["sums"]
    )
    worker.run()
    
Similarly, from the command line:

.. code-block:: bash
    
    export PROCRASTINATE_APP="mycode.app"
    
    procrastinate defer mycode.sum '{"a": 3, "b": 5}'
    
    procrastinate worker sums
    
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
