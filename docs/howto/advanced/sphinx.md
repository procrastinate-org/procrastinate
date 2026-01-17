# Document my tasks with Sphinx & Autodoc

If you use Sphinx's `autodoc` extension to document your project, you might
have noticed that your tasks are absent from the documentation. This is because
when you apply the `@app.task` decorator, you're actually replacing the
function with a Procrastinate Task object, which `autodoc` doesn't know how to
process.

Procrastinate provides a small Sphinx extension to fix that. You may want to
ensure procrastinate is installed with the `sphinx` extra in the environment
where you build your doc. This is not mandatory, as it only adds sphinx itself
as a dependency, but if the extension ever needs other dependencies in the
future, they will be installed through the `sphinx` extra as well.

```bash
$ pip install procrastinate[sphinx]
```

Then, add the following to your `conf.py`:

```python
extensions = [
    # ...
    "procrastinate.contrib.sphinx",
    # ...
]
```

That's it. Your tasks will now be picked up by `autodoc` and included in your
documentation.

:::{warning}
A [recent refactor](https://github.com/sphinx-doc/sphinx/issues/14089) of Autodoc in
`Sphinx>=9` broke the ability for Procrastinate to provide a working extension.
For now, a flag `autodoc_use_legacy_class_based` lets the extension use the legacy
implementation, and keep working. We don't know yet when this flag will be removed,
but by the time it is, it's quite probable that there will be a new API to make the
extension work. All in all this means that this extension still works, but does so
by changing a user-defined configuration flag, and it cannot know that this
won't affect the documentation in other ways (e.g. if other extensions require the
new implementation. This is unlikely for the time being.)

Please feel free to open a ticket if this ends up being a problem for you.
:::
