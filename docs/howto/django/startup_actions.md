# Run Procrastinate code at Django startup

If you need to interact with Procrastinate at startup, you may be tempted to
put some code directly at the top-level of a module, for it to run at import
time. The `procrastinate.contrib.django` app is not started yet and will
raise an error in this case. The recommended ways to do this is:

- Use the `PROCRASTINATE_ON_APP_READY` setting to run code when the app is
  ready (see {doc}`settings`).
- Use Django's [`AppConfig.ready()`] method to run your code when the app is
  started. In that case, ensure that the `procrastinate.contrib.django` app
  is located before your app in the `INSTALLED_APPS` list.

[`AppConfig.ready()`]: https://docs.djangoproject.com/en/5.0/ref/applications/#django.apps.AppConfig.ready
