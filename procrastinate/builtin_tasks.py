from typing import Optional

from procrastinate import store


def remove_old_jobs(
    job_store: store.BaseJobStore,
    max_hours: int,
    queue: Optional[str] = None,
    remove_error: Optional[bool] = False,
) -> None:
    """
    This task cleans your database by removing old jobs. Note that jobs and linked
    events will be irreversibly removed from the database when running this task.

    Parameters
    ----------
    max_hours :
        Only jobs which were finished more than ``max_hours`` ago will be deleted.
    queue :
        The name of the queue in which jobs will be deleted. If not specified, the
        task will delete jobs from all queues.
    remove_error :
        By default only successful jobs will be removed. When this parameter is True
        failed jobs will also be deleted.
    """
    job_store.delete_old_jobs(
        nb_hours=max_hours, queue=queue, include_error=remove_error
    )
