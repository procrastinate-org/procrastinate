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

    $ procrastinate

or:

.. code-block:: console

    $ python -m procrastinate

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

As a general rule, all parameters have an environment variable equivalent, named
``PROCRASTINATE_SOMETHING`` where ``SOMETHING`` is the uppercased long name of the
option, with ``-`` replaced with ``_``.

Logging
^^^^^^^

Three different options allow you to control how the command-line tool should log
events:

- Verbosity controls the log level (you'll see message of this level and above):

  +-------+---------------------------+-------------+
  | Flags | Environment equivalent    | Log level   |
  +=======+===========================+=============+
  |       | PROCRASTINATE_VERBOSITY=0 | ``warning`` |
  +-------+---------------------------+-------------+
  | -v    | PROCRASTINATE_VERBOSITY=1 | ``info``    |
  +-------+---------------------------+-------------+
  | -vv   | PROCRASTINATE_VERBOSITY=2 | ``debug``   |
  +-------+---------------------------+-------------+

- Log format: ``--log-format=`` / ``PROCRASTINATE_LOG_FORMAT=`` lets you control how
  the log line will be formatted. It uses ``%``-style placeholders by default.

- Log format style: ``--log-format-style=`` / ``PROCRASTINATE_LOG_FORMAT_STYLE=``
  lets you choose different styles for the log-format, such as ``{`` or ``$``.

For more information on log formats, refer to the `Python documentation`__

.. __: https://docs.python.org/3/library/logging.html?highlight=logging#logrecord-attributes
