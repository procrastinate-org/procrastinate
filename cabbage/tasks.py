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
import functools
import uuid
import psycopg2


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

        launch_task(queue=self.queue, name=self.name, lock=lock, kwargs=kwargs)

    def run(self, **kwargs):
        self.func(self, **kwargs)


def launch_task(queue, name, lock, kwargs):

    with get_global_connection().cursor() as cursor:
        cursor.execute(
            """INSERT INTO tasks (queue_id, task_type, targeted_object, args)
               SELECT id, %s, %s, %s FROM queues WHERE queue_name=%s;""",
            (name, lock, kwargs, queue),
        )


@functools.lru_cache(1)
def get_global_connection():
    conn = psycopg2.connect("")
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


class TaskManager:
    def __init__(self):
        self.tasks = {}

    def task(self, *args, **kwargs):
        task = Task(manager=self, *args, **kwargs)
        return task

    def register(self, task):
        self.tasks[task.name] = task
