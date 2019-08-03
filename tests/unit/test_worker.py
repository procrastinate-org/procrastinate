import sys

import pytest

from cabbage import exceptions, jobs, tasks, worker


def test_run(task_manager):
    class TestWorker(worker.Worker):
        i = 0

        def process_jobs(self):
            if self.i == 2:
                self.stop(None, None)
            self.i += 1

    test_worker = TestWorker(task_manager=task_manager, queues=["marsupilami"])

    test_worker.run(timeout=42)

    assert task_manager.job_store.listening_queues == {"marsupilami"}
    assert task_manager.job_store.waited == [42, 42]


def test_run_all_tasks(task_manager):
    class TestWorker(worker.Worker):
        def process_jobs(self):
            self.stop(None, None)

    test_worker = TestWorker(task_manager=task_manager)
    test_worker.run()

    assert task_manager.job_store.listening_all_queues is True


def test_process_jobs(mocker, task_manager, job_factory):
    job_1 = job_factory(id=42)
    job_2 = job_factory(id=43)
    job_3 = job_factory(id=44)
    job_4 = job_factory(id=45)
    task_manager.job_store.jobs = [job_1, job_2, job_3, job_4]

    test_worker = worker.Worker(task_manager, queues=["queue"])

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

    run_job = mocker.patch("cabbage.worker.Worker.run_job", side_effect=side_effect)

    test_worker.process_jobs()

    assert run_job.call_args_list == [
        mocker.call(job=job_1),
        mocker.call(job=job_2),
        mocker.call(job=job_3),
        mocker.call(job=job_4),
    ]

    assert task_manager.job_store.finished_jobs == [
        (job_1, jobs.Status.DONE),
        (job_2, jobs.Status.ERROR),
        (job_3, jobs.Status.ERROR),
        (job_4, jobs.Status.DONE),
    ]


def test_process_jobs_until_no_more_jobs(mocker, task_manager, job_factory):
    job = job_factory(id=42)
    task_manager.job_store.jobs = [job]

    mocker.patch("cabbage.worker.Worker.run_job")

    test_worker = worker.Worker(task_manager, queues=["queue"])
    test_worker.process_jobs()

    assert task_manager.job_store.finished_jobs == [(job, jobs.Status.DONE)]


def test_run_job(task_manager, job_store):
    result = []

    def task_func(a, b):  # pylint: disable=unused-argument
        result.append(a + b)

    task = tasks.Task(task_func, manager=task_manager, queue="yay", name="job")

    task_manager.tasks = {"task_func": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="task_func",
        queue="yay",
        job_store=job_store,
    )
    test_worker = worker.Worker(task_manager, queues=["yay"])
    test_worker.run_job(job)

    assert result == [12]


def test_run_job_log_result(caplog, task_manager, job_store):
    caplog.set_level("INFO")

    result = []

    def task_func(a, b):  # pylint: disable=unused-argument
        s = a + b
        result.append(s)
        return s

    task = tasks.Task(task_func, manager=task_manager, queue="yay", name="job")

    task_manager.tasks = {"task_func": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="task_func",
        queue="yay",
        job_store=job_store,
    )
    test_worker = worker.Worker(task_manager, queues=["yay"])
    test_worker.run_job(job)

    assert result == [12]

    records = [record for record in caplog.records if record.action == "job_success"]
    assert len(records) == 1
    record = records[0]
    assert record.result == 12


def test_run_job_error(task_manager, job_store):
    def job(a, b):  # pylint: disable=unused-argument
        raise ValueError("nope")

    task = tasks.Task(job, manager=task_manager, queue="yay", name="job")
    task.func = job

    task_manager.tasks = {"job": task}

    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="job",
        queue="yay",
        job_store=job_store,
    )
    test_worker = worker.Worker(task_manager, queues=["yay"])
    with pytest.raises(exceptions.JobError):
        test_worker.run_job(job)


def test_run_job_not_found(task_manager, job_store):
    job = jobs.Job(
        id=16,
        task_kwargs={"a": 9, "b": 3},
        lock="sherlock",
        task_name="job",
        queue="yay",
        job_store=job_store,
    )
    test_worker = worker.Worker(task_manager, queues=["yay"])
    with pytest.raises(exceptions.TaskNotFound):
        test_worker.run_job(job)


def test_import_all():
    module = "tests.unit.unused_module"
    assert module not in sys.modules

    worker.import_all([module])

    assert module in sys.modules


def test_worker_call_import_all(task_manager, mocker):

    import_all = mocker.patch("cabbage.worker.import_all")

    worker.Worker(task_manager=task_manager, queues=["yay"], import_paths=["hohoho"])

    import_all.assert_called_with(import_paths=["hohoho"])


def test_worker_load_task_known_missing(task_manager):
    task_worker = worker.Worker(task_manager=task_manager, queues=["yay"])

    task_worker.known_missing_tasks.add("foobarbaz")
    with pytest.raises(exceptions.TaskNotFound):
        task_worker.load_task("foobarbaz")


def test_worker_load_task_known_task(task_manager):
    task_worker = worker.Worker(task_manager=task_manager, queues=["yay"])

    @task_manager.task
    def task_func():
        pass

    assert task_worker.load_task("tests.unit.test_worker.task_func") == task_func


def test_worker_load_task_new_missing(task_manager):
    task_worker = worker.Worker(task_manager=task_manager, queues=["yay"])

    with pytest.raises(exceptions.TaskNotFound):
        task_worker.load_task("foobarbaz")

    assert task_worker.known_missing_tasks == {"foobarbaz"}


unknown_task = None


def test_worker_load_task_unknown_task(task_manager, caplog):
    global unknown_task
    task_worker = worker.Worker(task_manager=task_manager, queues=["yay"])

    @task_manager.task
    def task_func():
        pass

    unknown_task = task_func

    assert task_worker.load_task("tests.unit.test_worker.unknown_task") == task_func

    assert [record for record in caplog.records if record.action == "load_dynamic_task"]
