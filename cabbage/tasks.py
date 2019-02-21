import logging
import uuid

from cabbage import postgres

logger = logging.getLogger(__name__)


class Task:
    def __init__(self, manager, queue):
        self.queue = queue
        self.manager = manager

    def __call__(self, func):
        self.func = func
        self.name = func.__name__
        self.manager.register(self)
        return self

    def defer(self, lock=None, **kwargs):
        lock = lock or f"{uuid.uuid4()}"
        logger.info(
            f"Scheduling task {self.name} in queue {self.queue} with args {kwargs}"
        )
        postgres.launch_task(queue=self.queue, name=self.name, lock=lock, kwargs=kwargs)


class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.queues = set()

    def task(self, *args, **kwargs):
        task = Task(manager=self, *args, **kwargs)
        return task

    def register(self, task):
        self.tasks[task.name] = task
        if task.queue not in self.queues:
            logger.info(f"Creating queue {task.queue} (if not already existing)")
            postgres.register_queue(task.queue)
            self.queues.add(task.queue)


class TaskRun:
    def __init__(self, task, id, lock):
        self.task = task
        self.id = id
        self.lock = lock

    def run(self, **kwargs):
        self.task.func(self, **kwargs)
