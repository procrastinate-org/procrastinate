import pendulum
import pytest

from procrastinate import exceptions, jobs, tasks, worker


def test_run(app):
    class TestWorker(worker.Worker):
        i = 0

        def process_next_job(self):
            self.i += 1
            if self.i == 2:
                raise exceptions.NoMoreJobs
            elif self.i == 3:
                raise exceptions.StopRequested

    test_worker = TestWorker(app=app, queues=["marsupilami"])

    test_worker.run()

    assert app.job_store.queries == ["listen_for_jobs"]


@pytest.mark.parametrize(
    "side_effect, status",
    [
        (None, "succeeded"),
        (exceptions.JobError(), "failed"),
        (exceptions.TaskNotFound(), "failed"),
    ],
)
def test_process_next_job(mocker, app, job_factory, side_effect, status):
    job = job_factory(id=1)
    app.job_store.defer_job(job)

    test_worker = worker.Worker(app, queues=["queue"])

    run_job = mocker.patch(
        "procrastinate.worker.Worker.run_job", side_effect=side_effect
    )
    test_worker.process_next_job()

    run_job.assert_called_with(job=job)

    assert app.job_store.jobs[1]["status"] == status


def test_process_next_job_raise_no_more_jobs(app):
    test_worker = worker.Worker(app)

    with pytest.raises(exceptions.NoMoreJobs):
        test_worker.process_next_job()


def test_process_next_job_raise_stop_requested(app):
    test_worker = worker.Worker(app)

    @app.task
    def empty():
        test_worker.stop_requested = True

    empty.defer()

    with pytest.raises(exceptions.StopRequested):
        test_worker.process_next_job()


def test_process_next_job_retry_failed_job(mocker, app, job_factory):
    job = job_factory(id=1)
    app.job_store.defer_job(job)

    mocker.patch(
        "procrastinate.worker.Worker.run_job",
        side_effect=exceptions.JobRetry(
            scheduled_at=pendulum.datetime(2000, 1, 1, tz="UTC")
        ),
    )

    test_worker = worker.Worker(app, queues=["queue"])
    test_worker.process_next_job()

    new_job = app.job_store.jobs[1]
    assert len(app.job_store.jobs) == 1
    assert new_job["status"] == "todo"
    assert new_job["id"] == 1
    assert new_job["scheduled_at"] == pendulum.datetime(2000, 1, 1, tz="UTC")


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
    )
    test_worker = worker.Worker(app, queues=["yay"])
    with pytest.raises(exceptions.TaskNotFound):
        test_worker.run_job(job)


def test_worker_call_import_all(app, mocker):

    import_all = mocker.patch("procrastinate.utils.import_all")

    app.import_paths = ["hohoho"]

    worker.Worker(app=app, queues=["yay"])

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
