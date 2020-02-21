Use the command line
--------------------

Procrastinate installs a command-line tool, which allows to do
some operations:

- Prepare your database for procrastinate (apply the database schema)
- Launch a worker
- Defer a task
- ...

The command-line tool can be launched using:

.. code-block:: console

    $ procrastinate --help

or:

.. code-block:: console

    $ python -m procrastinate --help

Please read the included help to get familiar with its commands and parameters:

.. command-output:: procrastinate --help

Avoid specifying the ``--app`` parameter all the time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Procrastinate needs to know your app for most operations. in particular in the
command line interface, you'll find yourself frequently typing
``--app=dotted.path.to.app``. You can specify this one in your environment by instead
using:

.. code-block:: console

    $ export PROCRASTINATE_APP=dotted.path.to.app worker
