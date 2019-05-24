class CabbageException(Exception):
    pass


class TaskNotFound(CabbageException):
    pass


class NotATask(TaskNotFound):
    pass


class JobError(CabbageException):
    pass


class QueueNotFound(CabbageException):
    pass
