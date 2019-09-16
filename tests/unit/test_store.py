import pendulum
import pytest

from procrastinate import jobs


def test_store_defer(job_store, job_factory):
    job_row = job_store.defer_job(job=job_factory(task_kwargs={"a": "b"}))

    assert job_row == 1

    assert job_store.jobs == {
        1: {
            "args": {"a": "b"},
            "attempts": 0,
            "id": 1,
            "lock": None,
            "queue_name": "queue",
            "scheduled_at": None,
            "started_at": None,
            "status": "todo",
            "task_name": "bla",
        }
    }


def test_fetch_job_no_suitable_job(job_store):
    assert job_store.fetch_job(queues=None) is None


def test_fetch_job(job_store, job_factory):
    job = job_factory(id=1)
    job_store.defer_job(job=job)
    assert job_store.fetch_job(queues=None) == job


def test_get_stalled_jobs_not_stalled(job_store, job_factory):
    job = job_factory(id=1)
    job_store.defer_job(job=job)
    assert list(job_store.get_stalled_jobs(nb_seconds=1000)) == []


def test_get_stalled_jobs_stalled(job_store, job_factory):
    job = job_factory(id=1)
    job_store.defer_job(job=job)
    job_store.fetch_job(queues=None)
    job_store.jobs[1]["started_at"] = pendulum.datetime(2000, 1, 1)
    assert list(job_store.get_stalled_jobs(nb_seconds=1000)) == [job]


@pytest.mark.parametrize(
    "include_error, statuses",
    [(False, ("succeeded",)), (True, ("succeeded", "failed"))],
)
def test_delete_old_jobs(job_store, job_factory, include_error, statuses, mocker):

    job_store.execute_query = mocker.Mock()
    job_store.delete_old_jobs(
        nb_hours=5, queue="marsupilami", include_error=include_error
    )
    job_store.execute_query.assert_called_with(
        query=mocker.ANY, nb_hours=5, queue="marsupilami", statuses=statuses
    )


def test_finish_job(job_store, job_factory, mocker):

    job_store.execute_query = mocker.Mock()
    job = job_factory(id=1)
    retry_at = pendulum.datetime(2000, 1, 1)

    job_store.finish_job(job=job, status=jobs.Status.TODO, scheduled_at=retry_at)
    job_store.execute_query.assert_called_with(
        query=mocker.ANY, job_id=1, status="todo", scheduled_at=retry_at
    )


@pytest.mark.parametrize(
    "queues, queries",
    [
        (None, ["LISTEN procrastinate_any_queue;"]),
        (
            ["a", "b"],
            ["LISTEN procrastinate_queue#a;", "LISTEN procrastinate_queue#b;"],
        ),
    ],
)
def test_listen_for_jobs(job_store, mocker, queues, queries):
    job_store.execute_query = mocker.Mock()
    job_store.listen_for_jobs(queues)
    assert job_store.execute_query.call_args_list == [
        mocker.call(query=query) for query in queries
    ]
