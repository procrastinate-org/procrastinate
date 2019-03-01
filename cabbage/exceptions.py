class CabbageException(Exception):
    pass


class TaskNotFound(CabbageException):
    pass


class TaskError(CabbageException):
    pass


class QueueNotFound(CabbageException):
    pass
