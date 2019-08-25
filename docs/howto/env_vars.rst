Avoid specifying the ``--app`` parameter all the time
-----------------------------------------------------

Procrastinate needs to know your app for most operations. in particular in the
command line interface, you'll find yourself frequently typing
``--app=dotted.path.to.app``. You can specify this one in your environment by instead
using:

.. code-block:: console

    $ export PROCRASTINATE_APP=dotted.path.to.app worker
