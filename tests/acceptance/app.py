import procrastinate


app = procrastinate.App(job_store=procrastinate.PostgresJobStore(dsn='', dbname='procrastinate_test'))


@app.task(queue="default")
def sum_task(a, b):
    print(a + b)


@app.task()
def increment_task(a):
    print(a + 1)


@app.task(queue="product_queue")
def product_task(a, b):
    print(a * b)


nb_tries = 0


@app.task(queue="retry", retry=10)
def two_fails():
    global nb_tries
    if nb_tries < 2:
        nb_tries += 1
        raise Exception("This should fail")
