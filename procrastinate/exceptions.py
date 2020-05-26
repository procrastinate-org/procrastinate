import datetime


class ProcrastinateException(Exception):
    """
    Base type for all Procrastinate exceptions
    """

    pass


class TaskNotFound(ProcrastinateException):
    pass


class JobError(ProcrastinateException):
    pass


class LoadFromPathError(ImportError, ProcrastinateException):
    """
    Raised when calling :py:func:`procrastinate.App.from_path`
    when the app is not found or the object is not an App.
    """


class JobRetry(ProcrastinateException):
    def __init__(self, scheduled_at: datetime.datetime):
        self.scheduled_at = scheduled_at


class PoolAlreadySet(ProcrastinateException):
    """
    Indicates a call on connector.set_pool() was done but the
    pool already had a set. Changing the pool of a connector is not
    permitted.
    """

    pass


class ConnectorException(ProcrastinateException):
    """
    Any kind of database error will be raised as this type.
    The precise error can be seen with ``exception.__cause__``
    """

    pass


class AlreadyEnqueued(ProcrastinateException):
    """
    Indicates that there already is job waiting in the queue with the same queueing
    lock.
    """

    pass


class UniqueViolation(ConnectorException):
    """
    A unique constraint is violated. The constraint name is available in
    ``exception.constraint_name``. This is an internal exception.
    """

    def __init__(self, *args, constraint_name: str):
        super().__init__(*args)
        self.constraint_name = constraint_name

    pass
