# Configure Django & Procrastinate to work together

Many Django projects are deployed using PostgreSQL, so using procrastinate in
conjunction with Django would remove the necessity of having another broker to
schedule tasks.

## Configuration

To start, install procrastinate with:

```console
(venv) $ pip install 'procrastinate[django]'
```

Add procrastinate Django app to your `INSTALLED_APPS`. You may want to add it
before your own apps to ensure that procrastinate is ready before your own code
runs.

```python
INSTALLED_APPS = [
    ...
    "procrastinate.contrib.django",
    ...
]
```

## Configuring the app

An app will be configured for you in `procrastinate.contrib.django.app`.
You don't have to configure an app yourself.

You can modify the app after its creation, for example to load additional tasks from
blueprints, with:

```python
# settings.py
PROCRASTINATE_ON_APP_READY = "myapp.procrastinate.on_app_ready"
```
```python
# myapp/procrastinate.py
import procrastinate

def on_app_ready(app: procrastinate.App):
    app.add_tasks_from(some_blueprint)
```

:::{note}
While not recommended, you may decide to use a different app from the one
provided in `procrastinate.contrib.django.app`, it's not strictly incompatible,
but it might be more complicated and you may run into issues.
:::
