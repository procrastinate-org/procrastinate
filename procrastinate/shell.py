import cmd
import functools
from collections import Counter

from procrastinate.utils import sync_await


def async_wrap(coro):
    @functools.wraps(coro)
    def wrapper(*args, **kwargs):
        return sync_await(coro(*args, **kwargs))

    return wrapper


class ProcrastinateShell(cmd.Cmd):
    intro = 'Welcome to the procrastinate shell.   Type help or ? to list commands.\n'
    prompt = 'procrastinate> '

    def __init__(self, app):
        super().__init__()
        self.app = app

    def do_EOF(self, _):
        'Exit procrastinate shell'
        return True

    do_exit = do_EOF

    @async_wrap
    async def do_list_queues(self, _):
        sql = '''
        SELECT queue_name,
               COUNT(id) AS nb_jobs,
               (WITH stats AS (
                   SELECT status,
                          COUNT(*) AS nb_jobs
                     FROM procrastinate_jobs
                    WHERE queue_name = j.queue_name
                    GROUP BY status
                   )
                   SELECT json_object_agg(status, nb_jobs) FROM stats
               ) AS stats
          FROM procrastinate_jobs AS j
         GROUP BY queue_name
        '''
        for row in await self.app.job_store.execute_query_all(sql):
            jobs = Counter(row['stats'])
            print(f"{row['queue_name']}: {row['nb_jobs']} jobs (todo: {jobs['todo']}, succeeded: {jobs['succeeded']}, failed: {jobs['failed']})")
