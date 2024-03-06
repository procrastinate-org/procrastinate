# Interact with Procrastinate tables as Django models

Procrastinate exposes 3 of its internal tables as Django models. You can use
them to query the state of your jobs. They're also exposed in the Django admin.

:::{note}
We'll do our best to ensure backwards compatibility, but we won't always be
able to do so. If you use the models directly, make sure you test your
integration when upgrading Procrastinate.
:::

```python
from procrastinate.contrib.django.models import (
    ProcrastinateJob,
    ProcrastinateEvent,
    ProcrastinatePeriodicDefer,
)

ProcrastinateJob.objects.filter(task_name="mytask").count()
```

:::{note}
The models are read-only by default. You can't create, update or delete jobs
or events through the ORM.
:::

## Reference documentation


```{eval-rst}
.. automodule:: procrastinate.contrib.django.models
    :members: ProcrastinateJob, ProcrastinateEvent, ProcrastinatePeriodicDefer
```


## Making the models writable in tests

If you need to interact with the tables in your tests, a setting is provided:
`PROCASTINATE_READONLY_MODELS`. If set to `False`, the models will be writable.

:::{warning}
This is only intended for tests and should not be used for deferring or retrying
jobs in normal operation.
:::

:::{note}
This is not the only testing mechanism available. See {doc}`../testing` for more
features, potentially better suited for some kinds of tests and more details on
this setting.
:::
