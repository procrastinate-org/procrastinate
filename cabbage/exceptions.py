class CabbageException(Exception):
    pass


class TaskNotFound(CabbageException):
    pass


class JobError(CabbageException):
    pass


class LoadFromPathError(ImportError, CabbageException):
    pass


class JobStoreNotFound(CabbageException):
    pass
