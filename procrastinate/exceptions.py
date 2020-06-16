import datetime


class ProcrastinateException(Exception):
    """
    Unexpected Procrastinate error.
    """

    def __init__(self, message=None):
        if not message:
            message = self.__doc__
        super().__init__(message)


class TaskNotFound(ProcrastinateException):
    """
    Task cannot be imported.
    """


class JobError(ProcrastinateException):
    """
    Job ended with an exception.
    """


class LoadFromPathError(ImportError, ProcrastinateException):
    """
    App was not found at the provided path, or the loaded object is not an App.
    """


class JobRetry(ProcrastinateException):
    """
    Job should be retried.
    """

    def __init__(self, scheduled_at: datetime.datetime):
        self.scheduled_at = scheduled_at
        super().__init__()


class PoolAlreadySet(ProcrastinateException):
    """
    connector.set_pool() was called but the pool already had a set.
    Changing the pool of a connector is not permitted.
    """


class ConnectorException(ProcrastinateException):
    """
    Database error.
    """

    # The precise error can be seen with ``exception.__cause__``.


class AlreadyEnqueued(ProcrastinateException):
    """
    There is already a job waiting in the queue with the same queueing lock.
    """


class UniqueViolation(ConnectorException):
    """
    A unique constraint is violated. The constraint name is available in
    ``exception.constraint_name``.
    """

    def __init__(self, *args, constraint_name: str):
        super().__init__(*args)
        self.constraint_name = constraint_name


class MissingApp(ProcrastinateException):
    """
    Missing app. This most probably happened because procrastinate needs an
    app via --app or the PROCRASTINATE_APP environment variable.
    """


class SyncConnectorConfigurationError(ProcrastinateException):
    """
    A synchronous connector (probably Psycopg2Connector) was used, but the operation
    needs an asynchronous connector (AiopgConnector). Please check your App
    configuration.
    """
