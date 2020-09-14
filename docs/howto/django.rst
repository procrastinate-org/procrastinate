Use Procrastinate in a Django application
=========================================

Install procrastinate with:

.. code-block:: console

    $ (venv) pip install 'procrastinate[django]'

This tells pip to consider the extra dependencies from the group of dependencies named
``django``. For now, this group only contains Django itself, which you likely already
have in your project's dependencies. So why bother?

Specifying your dependency to the "``django`` extras" will ensure that your Django version
and the one we support stay in sync through time (for now, we support every version, but
if we learn of strong incompatibilities, we'll update the lib: we're considering every
version is compatible until proven otherwise). Also, while this is not the case today,
if our Django integration ever requires other third-party packages, they will be added
here.

Add Procrastinate in your ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        "procrastinate.contrib.django",
    ]

Configure your procrastinate app from your Django settings::

    import procrastinate
    from procrastinate.contrib.django import connector_params

    app = procrastinate.App(
        connector=procrastinate.Psycopg2Connector(**connector_params())
    )

(See `connector` for more on how to instanciate your connector.)

Procrastinate comes with its own migrations so don't forget to run ``./manage.py
migrate``.
