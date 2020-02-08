Find a correct place for your app
---------------------------------

We advise you to place your app in one of the following places:

- Your program ``__init__`` or the place where you define your top level objects,
- A dedicated module (``yourapp.procrastinate`` for example),
- The place where you define all your tasks if it's a single module.

In the first two cases, it's important to specify the location to your tasks using the
``import_paths`` parameter::

    import procrastinate

    app = procrastinate.App(
        connector=connector,
        import_paths=["dotted.path.to", "all.the.modules", "that.define.tasks"]
    )
