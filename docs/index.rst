Cabbage: Postgresql-based Task Queue for Python
===============================================

Cabbage is an open-source Python 3.6+ distributed task processing library,
leveraging postgresql to store task definitions, manage locks and
dispatch tasks.

Here's an example::

    # Make a app in your code
    app = cabbage.App()

    # Then define tasks
    @app.task(queue="sums")
    def sum(a, b):
        with open("myfile", "w") as f:
            f.write(str(a + b))

    # Launch tasks
    sum.defer(a=3, b=5)

    # Somewhere in your program, launch a worker
    worker = cabbage.Worker(
        app=app,
        queues=["sums"]
    )
    worker.run()

There are quite a few interesting features that Cabbage adds to the mix.
You can head to the Quickstart section for a general tour or
to the How-To sections for specific features. The Discussion
section should hopefully answer your questions. Otherwise,
feel free to open an `issue <https://github.com/peopledoc/cabbage/issues>`_.

.. toctree::
   :maxdepth: 2

   quickstart
   howto
   discussions
   reference



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
