Use Procrastinate in a Django application
=========================================

Install procrastinate with:

.. code-block:: console

    $ (venv) pip install 'procrastinate[django]'

This tells pip to install procrastinate and consider the extra dependencies
from the group of dependencies named ``django``. For now, this group only
contains Django itself, which you likely already have in your project's
dependencies. So why bother?

Specifying your dependency to the "``django`` extras" will ensure that your
Django version and the one we support stay in sync through time (for now, we
support every version, but if we learn of strong incompatibilities, we'll
update the lib: we're considering every version is compatible until proven
otherwise). Also, while this is not the case today, if our Django integration
ever requires other third-party packages, they will be added here.

Add procrastinate Django app to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "procrastinate.contrib.django",
    ]


After that, you need to create a new directory to contain the procrastinate
app, where you will define your tasks. This app will run independently of
Django but will be able to access the whole Django ecosystem (it's not a Django
app, nor will be inside any of your existing Django apps). Create a new
directory ``tasks`` and fill the ``tasks/__init__.py`` with:

.. code-block:: python

    import django
    django.setup()  # Setup Django inside the worker so you can import/use ORM etc.

    from procrastinate import App, AiopgConnector
    from procrastinate.contrib.django import connector_params

    from myapp.models import MyModel


    app = App(connector=AiopgConnector(**connector_params()))
    app.open()

    @app.task(name="mytask")
    def mytask(obj_pk):
        print(f"Executing mytask for object {obj_pk}...")
        obj = MyModel.objects.get(pj=obj_pk)
        ...

To run the procrastinate worker properly, you need to set
``DJANGO_SETTINGS_MODULE`` to your project's settings module and point to the
``tasks`` app you just created:

.. code-block:: console

    DJANGO_SETTINGS_MODULE=myproj.settings PYTHONPATH=. procrastinate --app=tasks.app worker

Note that ``tasks`` won't be a Django app (so Django won't import it), but you
still need to be able to launch tasks from your Django code (for example,
inside a view). Since the procrastinate app is not imported by Django, you must
create a new ``app`` object accessible via Django to launch tasks (this object
won't act like a worker, it's just your bridge from Django so you can launch
tasks). Select an app and create ``myapp/tasks.py`` file with the following
contents:

.. code-block:: python

    """Expose procrastinate tasks so Django apps can call them"""

    from procrastinate import App, Psycopg2Connector
    from procrastinate.contrib.django import connector_params

    # Depending on how the Django-postgres connection is configured, you may
    # change the connector to `AiopgConnector`
    app = App(connector=Psycopg2Connector(**connector_params()))
    app.open()

    # Task functions
    mytask = app.configure_task(name="mytask")

(See `connector` for more on how to instantiate your connector.)

Now you can finally launch this task from your ``myapp/views.py``:

.. code-block:: python

    from myapp.tasks import mytask

    def myview(request):
        ...
        mytask.defer(obj_pk=obj.pk)


Procrastinate comes with its own migrations so don't forget to run
``./manage.py migrate``.

There are still some `pending issues`_ to improve procrastinate Django
experience, feel free to `contribute`_! Additionally, it's worth noting that
there are other Python job scheduling libraries based on postgres'
LISTEN/NOTIFY that integrate with Django. For instance, `django-pgpubsub`_ is
more focused on Django, although it is still in the early stages of
development.

.. _contribute: https://github.com/procrastinate-org/procrastinate/blob/main/CONTRIBUTING.rst
.. _pending issues: https://github.com/procrastinate-org/procrastinate/issues?q=is%3Aissue+is%3Aopen+django
.. _django-pgpubsub: https://readthedocs.org/projects/django-pgpubsub/
