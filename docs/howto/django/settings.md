# Customize the app integration through settings

Procrastinate exposes a few Django settings:

```python
# Dotted path to a function to run when the app is ready (see below).
PROCRASTINATE_ON_APP_READY: str

# By default, the `tasks` module in each app is auto-discovered for tasks.
# You can change the name `tasks`` to something else, and add additional paths.

# Change the name of the module where tasks are auto-discovered.
# If set to None, auto-discovery is disabled except for paths in IMPORT_PATHS.
PROCRASTINATE_AUTODISCOVER_MODULE_NAME: str | None  # (defaults to "tasks")
# Dotted paths to additional modules containing tasks.
PROCRASTINATE_IMPORT_PATHS: list[str]  # (defaults  to [])

# If you just want to change the database alias used by the connector,
# you can use this setting.
PROCRASTINATE_DATABASE_ALIAS: str,  # (defaults to "default")

# These settings are passed as-is to the App constructor.
PROCRASTINATE_WORKER_DEFAULTS: dict | None,  # (defaults to None)
PROCRASTINATE_PERIODIC_DEFAULTS: dict | None,  # (defaults to None)

# To be used only in settings. Enables/disables the read-only protection of
# the models (see the doc pages on tests).
PROCRASTINATE_READONLY_MODELS: bool  # (defaults to True)
```

## `PROCRASTINATE_ON_APP_READY`
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
