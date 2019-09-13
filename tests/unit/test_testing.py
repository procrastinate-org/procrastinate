import pendulum
import pytest

from procrastinate import jobs


def test_reset(job_store, job_factory):
    job_store.jobs = job_factory()
    job_store.reset()
    assert job_store.jobs == []


def test_launch_job(job_store, job_factory):
    job1 = job_store.defer_job(job_factory())
    job2 = job_store.defer_job(job_factory())

    assert job1 == 1
    assert job2 == 2

    assert [job.id for job in job_store.jobs] == [1, 2]


@pytest.mark.parametrize(
    "job",
    [
        jobs.Job(
            id=2,
            queue="queue_a",
            task_name="task_2",
            lock="lock_2",
            task_kwargs={"c": "d"},
        ),
        jobs.Job(
            id=2,
            queue="queue_a",
            task_name="task_3",
            lock="lock_3",
            task_kwargs={"i": "j"},
            scheduled_at=pendulum.datetime(2000, 1, 1),
        ),
    ],
)
def test_get_job(job_store, job):
    # Add a first started job
    job_store.defer_job(
        jobs.Job(
            id=1,
            queue="queue_a",
            task_name="task_1",
            lock="lock_1",
            task_kwargs={"a": "b"},
        )
    )
    job_store.get_job(queues=None)

    # Now add the job we're testing
    job_store.defer_job(job)

    assert job_store.get_job(queues=["queue_a"]) == job


@pytest.mark.parametrize(
    "job",
    [
        # We won't see this one because of the lock
        jobs.Job(
            id=2,
            queue="queue_a",
            task_name="task_2",
            lock="lock_1",
            task_kwargs={"e": "f"},
        ),
        # We won't see this one because of the queue
        jobs.Job(
            id=2,
            queue="queue_b",
            task_name="task_3",
            lock="lock_3",
            task_kwargs={"i": "j"},
        ),
        # We won't see this one because of the scheduled date
        jobs.Job(
            id=2,
            queue="queue_a",
            task_name="task_4",
            lock="lock_4",
            task_kwargs={"i": "j"},
            scheduled_at=pendulum.datetime(2100, 1, 1),
        ),
    ],
)
def test_get_job_no_result(job_store, job):
    # Add a first started job
    job_store.defer_job(
        jobs.Job(
            id=1,
            queue="queue_a",
            task_name="task_1",
            lock="lock_1",
            task_kwargs={"a": "b"},
        )
    )
    job_store.get_job(queues=None)

    # Now add the job we're testing
    job_store.defer_job(job)

    assert job_store.get_job(queues=["queue_a"]) is None


@pytest.mark.parametrize("status", [jobs.Status.SUCCEEDED, jobs.Status.FAILED])
def test_finish_job_finished(job_factory, job_store, status):

    job_store.defer_job(job_factory(id=1))
    job = job_store.get_job(queues=None)
    job_store.finish_job(job=job, status=status)

    assert job_store.jobs == []
    assert job_store.finished_jobs == [(job, status)]


def test_finish_job_retried(job_factory, job_store):

    job_store.defer_job(job_factory(id=1))
    job = job_store.get_job(queues=None)
    job_store.finish_job(job=job, status=jobs.Status.TODO)

    new_job, = job_store.jobs
    assert new_job.attempts == job.attempts + 1


def test_listen_for_jobs_all_queues(job_store):
    job_store.listen_for_jobs(queues=None)
    assert job_store.listening_all_queues is True


def test_listen_for_jobs(job_store):
    job_store.listen_for_jobs(queues=["a", "b"])
    assert job_store.listening_queues == {"a", "b"}


def test_wait_for_jobs(job_store):
    job_store.wait_for_jobs()
    assert job_store.waited is True


def test_execute_queries(job_store):
    job_store.execute_queries("foobar")
    assert job_store.queries == ["foobar"]


def test_stop(job_store):
    # If we don't crash, it's enough
    job_store.stop()
