Quickstart
==========

In this section, we're going to build together a small application showcasing
Procrastinate and its everyday use.

Prerequisites & installation
----------------------------

If you already have a PostgreSQL database around, make sure to note the connection
parameters. Otherwise, we'll create one together with Docker_, but is works all the
same if you'd rather install PostgreSQL directly in your system.

.. _Docker: https://docs.docker.com/

.. code-block:: console

    $ docker run --detach --rm -p 5432:5432 postgres

.. note::

    If you need to stop the docker at some point, use ``docker ps`` to find the
    container id and ``docker stop {container_id}``.
