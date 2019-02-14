"""
insert into queues (queue_name) values ('toto');

LISTEN "queue#toto";

insert into tasks (queue_id, task_type, targeted_object) values (1, 'expire machin', 'mon:objet#42');
-- Asynchronous notification "queue#toto" with payload "expire machin" received from server process with PID 13917.

select * from fetch_task('toto');
 id | queue_id |   task_type   | targeted_object | status
----+----------+---------------+-----------------+--------
  2 |        1 | expire machin | mon:objet#42    | doing
(1 row)


select finish_task(2, 'done');

"""
import logging
import functools
import uuid
import psycopg2

logger = logging.getLogger(__name__)


class Task:
    def __init__(self, manager, queue):
        self.queue = queue
        self.manager = manager

    def __call__(self, func=None, **kwargs):
        self.func = func
        self.name = func.__name__
        self.manager.register(self)
        return self

    def defer(self, lock=None, **kwargs):
        lock = lock or f"{uuid.uuid4()}"
        logger.info(
            f"Scheduling task {self.name} in queue {self.queue} with args {kwargs}"
        )
        launch_task(queue=self.queue, name=self.name, lock=lock, kwargs=kwargs)


def launch_task(queue, name, lock, kwargs):

    conn = get_global_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO tasks (queue_id, task_type, targeted_object, args)
               SELECT id, %s, %s, %s FROM queues WHERE queue_name=%s;""",
            (name, lock, kwargs, queue),
        )
    conn.commit()


def register_queue(queue):
    conn = get_global_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO queues (queue_name) VALUES (%s) ON CONFLICT DO NOTHING""",
            (queue,),
        )
    conn.commit()


@functools.lru_cache(1)
def get_global_connection():
    conn = psycopg2.connect("")
    # conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)
    return conn


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
            register_queue(task.queue)
            self.queues.add(task.queue)


class TaskRun:
    def __init__(self, task, id, lock):
        self.task = task
        self.id = id
        self.lock = lock

    def run(self, **kwargs):
        self.task.func(self, **kwargs)
