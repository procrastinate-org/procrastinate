import pytest

from cabbage import exceptions, jobs, task_worker, tasks, testing


@pytest.fixture
def manager(mocker):
    return tasks.TaskManager(job_store=testing.InMemoryJobStore())


@pytest.fixture
def job_factory():
    defaults = {
        "id": 42,
        "task_name": "bla",
        "kwargs": {},
        "lock": None,
        "queue": "queue",
    }

    def factory(**kwargs):
        final_kwargs = defaults.copy()
        final_kwargs.update(kwargs)
        return jobs.Job(**final_kwargs)

    return factory


def test_run(manager, mocker):
    class TestTaskWorker(task_worker.Worker):
        i = 0

        def process_tasks(self):
            if self.i == 2:
                self.stop(None, None)
            self.i += 1

    worker = TestTaskWorker(task_manager=manager, queue="marsupilami")

    worker.run(timeout=42)

    manager.job_store.listening_queues == {"marsupilami"}
    manager.job_store.waited == [42]


def test_process_tasks(mocker, manager, job_factory):
    job_1 = job_factory(id=42)
    job_2 = job_factory(id=43)
    job_3 = job_factory(id=44)
    manager.job_store.jobs["queue"] = [job_1, job_2, job_3]
    worker = task_worker.Worker(manager, "queue")

    i = 0

    def side_effect(job):
        nonlocal i
        i += 1
        if i == 1:
            # First time the task runs
            return None
        elif i == 2:
            # Then the task fails
            raise exceptions.TaskError()
        else:
            # While the third task runs, a stop signal is received
            worker.stop(None, None)

    call_task = mocker.patch(
        "cabbage.task_worker.Worker.run_task", side_effect=side_effect
    )
    worker.process_tasks()

    assert call_task.call_args_list == [
        mocker.call(job=job_1),
        mocker.call(job=job_2),
        mocker.call(job=job_3),
    ]

    assert manager.job_store.finished_jobs == [
        (job_1, jobs.Status.DONE),
        (job_2, jobs.Status.ERROR),
        (job_3, jobs.Status.DONE),
    ]


def test_run_task(manager):
    result = []

    def job(a, b):  # pylint: disable=unused-argument
        result.append(a + b)

    task = tasks.Task(job, manager=manager, queue="yay", name="job")

    manager.tasks = {"job": task}

    row = jobs.Job(
        id=16, kwargs={"a": 9, "b": 3}, lock="sherlock", task_name="job", queue="yay"
    )
    worker = task_worker.Worker(manager, "yay")
    worker.run_task(row)

    assert result == [12]


def test_run_task_error(manager):
    def job(a, b):  # pylint: disable=unused-argument
        raise ValueError("nope")

    task = tasks.Task(job, manager=manager, queue="yay", name="job")
    task.func = job

    manager.tasks = {"job": task}

    row = jobs.Job(
        id=16, kwargs={"a": 9, "b": 3}, lock="sherlock", task_name="job", queue="yay"
    )
    worker = task_worker.Worker(manager, "yay")
    with pytest.raises(exceptions.TaskError):
        worker.run_task(row)


def test_run_task_not_found(manager):
    row = jobs.Job(
        id=16, kwargs={"a": 9, "b": 3}, lock="sherlock", task_name="job", queue="yay"
    )
    worker = task_worker.Worker(manager, "yay")
    with pytest.raises(exceptions.TaskNotFound):
        worker.run_task(row)
