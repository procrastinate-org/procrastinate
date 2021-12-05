Create modular collections of tasks by using Blueprints
-------------------------------------------------------

Procrastinate provides Blueprints as a way to factor a large number of tasks
into smaller self contained collections.

You may want to create a collection for simple organsational reasons within the
same project. Or you may want to maintain a collection of tasks in a seperate
package which is maintained independently of your Procrastinate codebase::

    ...

    from my_external_package import tasks_blueprint
    ...

    app.add_tasks_from(tasks_blueprint, namespace="my_external_package")


Blueprints are easy to use, and task creation follows the pattern and API as
`App.task`.

Firstly, create a Blueprint instance and then create some tasks::

    from procrastinate import Blueprint

    my_blueprint = Blueprint()

    @my_blueprint.task()
    def mytask(argument, other_argument):
        ...

In your projcet register the blueprint with the `App` after you have created it::

    from procrastinate import AiopgConnector, App

    app = App(connector=AiopgConnector())

    app.add_tasks_from(my_blueprint, namespace="unique_name")
