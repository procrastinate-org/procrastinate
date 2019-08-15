import datetime


class procrastinateException(Exception):
    pass


class TaskNotFound(procrastinateException):
    pass


class JobError(procrastinateException):
    pass


class LoadFromPathError(ImportError, procrastinateException):
    pass


class JobRetry(procrastinateException):
    def __init__(self, scheduled_at: datetime.datetime):
        self.scheduled_at = scheduled_at
