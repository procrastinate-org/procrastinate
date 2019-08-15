import sys

import pendulum
import pytest

from procrastinate import exceptions, jobs, tasks, worker


def test_run(app):
    class TestWorker(worker.Worker):
        i = 0

        def process_jobs_once(self):
            if self.i == 2:
                self.stop(None, None)
            self.i += 1

    test_worker = TestWorker(app=app, queues=["marsupilami"])

    test_worker.run()

    assert app.job_store.listening_queues == {"marsupilami"}
    assert app.job_store.waited is True


def test_run_all_tasks(app):
    class TestWorker(worker.Worker):
        def process_jobs_once(self):
            self.stop(None, None)

    test_worker = TestWorker(app=app)
    test_worker.run()

    assert app.job_store.listening_all_queues is True


def test_process_jobs_once(mocker, app, job_factory):
    job_1 = job_factory(id=42)
    job_2 = job_factory(id=43)
    job_3 = job_factory(id=44)
    job_4 = job_factory(id=45)
    app.job_store.jobs = [job_1, job_2, job_3, job_4]

    test_worker = worker.Worker(app, queues=["queue"])

    i = 0

    def side_effect(job):
        nonlocal i
        i += 1
        if i == 1:
            # First time the task runs
            return None
        elif i == 2:
            # Then the task fails
            raise exceptions.JobError()
        elif i == 3:
            # Then the task fails
            raise exceptions.TaskNotFound()
        else:
            # While the third task runs, a stop signal is received
            test_worker.stop(None, None)

    run_job = mocker.patch(
        "procrastinate.worker.Worker.run_job", side_effect=side_effect
    )

    test_worker.process_jobs_once()

    assert run_job.call_args_list == [
        mocker.call(job=job_1),
        mocker.call(job=job_2),
        mocker.call(job=job_3),
        mocker.call(job=job_4),
    ]

    assert app.job_store.finished_jobs == [
        (job_1, jobs.Status.DONE),
        (job_2, jobs.Status.ERROR),
        (job_3, jobs.Status.ERROR),
        (job_4, jobs.Status.DONE),
    ]


def test_process_jobs_once_until_no_more_jobs(mocker, app, job_factory):
    job = job_factory(id=42)
    app.job_store.jobs = [job]

    mocker.patch("procrastinate.worker.Worker.run_job")

    test_worker = worker.Worker(app, queues=["queue"])
    test_worker.process_jobs_once()

    assert app.job_store.finished_jobs == [(job, jobs.Status.DONE)]


def test_process_jobs_once_retry_failed_job(mocker, app, job_factory):
    job = job_factory(id=42)
    app.job_store.jobs = [job]

    mocker.patch(
        "procrastinate.worker.Worker.run_job",
        side_effect=exceptions.JobRetry(
            scheduled_at=pendulum.datetime(2000, 1, 1, tz="UTC")
        ),
    )

    test_worker = worker.Worker(app, queues=["queue"])
    test_worker.process_jobs_once()

    assert app.job_store.finished_jobs == []
    assert len(app.job_store.jobs) == 1
    new_job = app.job_store.jobs[0]
    assert new_job.id == 42
    assert new_job.scheduled_at == pendulum.datetime(2000, 1, 1, tz="UTC")


def test_run_job(app, job_store):
    result = []

    def task_func(a, b):  # pylint: disable=unused-argument
        result.append(a + b)

    task = tasks.Task(task_func, app=app, queue="yay", name="job")

    app.tasks = {"task_func": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="task_func",
        queue="yay",
        job_store=job_store,
    )
    test_worker = worker.Worker(app, queues=["yay"])
    test_worker.run_job(job)

    assert result == [12]


def test_run_job_log_result(caplog, app, job_store):
    caplog.set_level("INFO")

    result = []

    def task_func(a, b):  # pylint: disable=unused-argument
        s = a + b
        result.append(s)
        return s

    task = tasks.Task(task_func, app=app, queue="yay", name="job")

    app.tasks = {"task_func": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="task_func",
        queue="yay",
        job_store=job_store,
    )
    test_worker = worker.Worker(app, queues=["yay"])
    test_worker.run_job(job)

    assert result == [12]

    records = [record for record in caplog.records if record.action == "job_success"]
    assert len(records) == 1
    record = records[0]
    assert record.result == 12


def test_run_job_error(app, job_store):
    def job(a, b):  # pylint: disable=unused-argument
        raise ValueError("nope")

    task = tasks.Task(job, app=app, queue="yay", name="job")
    task.func = job

    app.tasks = {"job": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="job",
        queue="yay",
        job_store=job_store,
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.JobError):
        test_worker.run_job(job)


def test_run_job_retry(app, job_store):
    def job(a, b):  # pylint: disable=unused-argument
        raise ValueError("nope")

    task = tasks.Task(job, app=app, queue="yay", name="job", retry=True)
    task.func = job

    app.tasks = {"job": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="job",
        queue="yay",
        job_store=job_store,
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.JobRetry):
        test_worker.run_job(job)


def test_run_job_not_found(app, job_store):
    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="job",
        queue="yay",
        job_store=job_store,
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.TaskNotFound):
        test_worker.run_job(job)


def test_import_all():
    module = "tests.unit.unused_module"
    assert module not in sys.modules

    worker.import_all([module])

    assert module in sys.modules


def test_worker_call_import_all(app, mocker):

    import_all = mocker.patch("procrastinate.worker.import_all")

    worker.Worker(app=app, queues=["yay"], import_paths=["hohoho"])

    import_all.assert_called_with(import_paths=["hohoho"])


def test_worker_load_task_known_missing(app):
    task_worker = worker.Worker(app=app, queues=["yay"])

    task_worker.known_missing_tasks.add("foobarbaz")
    with pytest.raises(exceptions.TaskNotFound):
        task_worker.load_task("foobarbaz")


def test_worker_load_task_known_task(app):
    task_worker = worker.Worker(app=app, queues=["yay"])

    @app.task
    def task_func():
        pass

    assert task_worker.load_task("tests.unit.test_worker.task_func") == task_func


def test_worker_load_task_new_missing(app):
    task_worker = worker.Worker(app=app, queues=["yay"])

    with pytest.raises(exceptions.TaskNotFound):
        task_worker.load_task("foobarbaz")

    assert task_worker.known_missing_tasks == {"foobarbaz"}


unknown_task = None


def test_worker_load_task_unknown_task(app, caplog):
    global unknown_task
    task_worker = worker.Worker(app=app, queues=["yay"])

    @app.task
    def task_func():
        pass

    unknown_task = task_func

    assert task_worker.load_task("tests.unit.test_worker.unknown_task") == task_func

    assert [record for record in caplog.records if record.action == "load_dynamic_task"]
