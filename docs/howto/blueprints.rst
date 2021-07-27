Use Blueprints
--------------

You can use blueprints to break up your tasks.

Firstly use blueprints to create a task collection::

    from procrastinate import Blueprint

    bp = Blueprint()

    @bp.task()
    def mytask(argument, other_argument):
        ...

Then register blueprint with the app after you have created it::

    from procrastinate import AiopgConnector, App

    app = App(connector=AiopgConnector())

    app.register_blueprint(bp)

Blueprint tasks take the same arguments as `App.task`.
