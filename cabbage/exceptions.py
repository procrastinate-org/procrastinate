import datetime


class CabbageException(Exception):
    pass


class TaskNotFound(CabbageException):
    pass


class JobError(CabbageException):
    pass


class LoadFromPathError(ImportError, CabbageException):
    pass


class JobRetry(CabbageException):
    def __init__(self, scheduled_at: datetime.datetime):
        self.scheduled_at = scheduled_at
