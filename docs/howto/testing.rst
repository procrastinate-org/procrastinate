Test your code that uses Procrastinate
--------------------------------------

Procrastinate defines an `InMemoryJobStore` that will speed up your tests,
remove dependency to PostgreSQL and allow you to have tasks run in a
controlled way.

To use it, you can do::

    app = procrastinate.App(job_store=procrastinate.testing.InMemoryJobStore())

    # Run the jobs your tests created, then stop
    # the worker:
    app.run_worker(only_once=True)

    # See the jobs created:
    print(app.job_store.jobs)

    # Reset the store between tests:
    app.job_store.reset()
