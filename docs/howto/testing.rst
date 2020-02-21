Test your code that uses Procrastinate
--------------------------------------

Procrastinate defines an `InMemoryConnector` that will speed up your tests,
remove dependency to PostgreSQL and allow you to have tasks run in a
controlled way.

To use it, you can do::

    app = procrastinate.App(connector=procrastinate.testing.InMemoryConnector())

    # Run the jobs your tests created, then stop the worker
    app.run_worker(wait=False)

    # See the jobs created:
    print(app.connector.jobs)

    # Reset the store between tests:
    app.connector.reset()
