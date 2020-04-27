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
