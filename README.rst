Procrastinate: PostgreSQL-based Task Queue for Python
=====================================================

.. image:: https://badge.fury.io/py/procrastinate.svg
    :target: https://pypi.org/pypi/procrastinate
    :alt: Deployed to PyPI

.. image:: https://travis-ci.org/peopledoc/procrastinate.svg?branch=master
    :target: https://travis-ci.org/peopledoc/procrastinate
    :alt: Continuous Integration Status

.. image:: https://codecov.io/gh/peopledoc/procrastinate/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/peopledoc/procrastinate
    :alt: Coverage Status

.. image:: https://readthedocs.org/projects/procrastinate/badge/?version=latest
    :target: http://procrastinate.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :target: https://github.com/peopledoc/procrastinate/blob/master/LICENSE
    :alt: MIT License


Procrastinate is an open-source Python 3.6+ distributed task processing
library, leveraging PostgreSQL to store task definitions, manage locks and
dispatch tasks. The project is still quite early-stage and will probably evolve.

Here's an example::

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

There are quite a few interesting features that Procrastinate adds to the mix.
You can head to the Quickstart section for a general tour or
to the How-To sections for specific features. The Discussion
section should hopefully answer your questions. Otherwise,
feel free to open an `issue <https://github.com/peopledoc/procrastinate/issues>`_.

*Note to my future self: add a quick note here on why this project is named*
"Procrastinate_".

.. _Procrastinate: https://en.wikipedia.org/wiki/Procrastination

.. Below this line is content specific to the README that will not appear in the doc.
.. end-of-index-doc

Where to go from here
---------------------

The complete docs_ is probably the best place to learn about
