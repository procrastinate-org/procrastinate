from procrastinate import builtin_tasks


def test_remove_old_jobs(mocker):
    mock_job_store = mocker.Mock()
    mock_delete_jobs = mock_job_store.delete_old_jobs

    builtin_tasks.remove_old_jobs(
        mock_job_store, max_hours=2, queue="queue_a", remove_error=True
    )
    assert mock_delete_jobs.call_args_list == [
        mocker.call(nb_hours=2, queue="queue_a", include_error=True)
    ]
