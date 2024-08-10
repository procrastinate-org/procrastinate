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
