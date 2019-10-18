import pytest

from procrastinate import exceptions, worker


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

    assert task_worker.load_task("tests.unit.test_worker_sync.task_func") == task_func


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

    assert (
        task_worker.load_task("tests.unit.test_worker_sync.unknown_task") == task_func
    )

    assert [record for record in caplog.records if record.action == "load_dynamic_task"]
