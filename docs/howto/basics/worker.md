# Launch a worker

You can either go towards the CLI route with:

```console
$ procrastinate --verbose --app=dotted.path.to.app worker [--name=worker-name] [queue [...]]
```

or, identically, use the code way:

```
app.run_worker(queues=["queue", ...], name="worker-name")
# or
await app.run_worker_async(queues=["queue", ...], name="worker-name")
```

In both cases, not specifying queues will tell Procrastinate to listen to every queue.
Naming the worker is optional.

:::{note}
{py:meth}`App.run_worker` will take care of launching an event loop, opening the app,
running the worker, and when it exists, closing the app and the event loop.

On the other hand, {py:meth}`App.run_worker_async` needs to run while the app is open.
The CLI takes care of opening the app.
:::

## ... Inside an application

When running the worker inside a bigger application, you may want to use
`install_signal_handlers=False` so that the worker doesn't interfere with
your application's signal handlers.

:::{note}
When you run the worker as a task, at any point, you can call `task.cancel()`
to request the worker to gracefully stop at the next opportunity.
You may then wait for it to actually stop using `await task` if you're
ready to wait indefinitely, or `asyncio.wait_for(task, timeout)` if you
want to set a timeout.
:::

Here is an example FastAPI application that does this:

```python
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from procrastinate import App, PsycopgConnector

logging.basicConfig(level=logging.DEBUG)


task_queue = App(connector=PsycopgConnector())


@task_queue.task
async def sleep(length):
    await asyncio.sleep(length)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with task_queue.open_async():
        worker = asyncio.create_task(
            task_queue.run_worker_async(install_signal_handlers=False)
        )
        # Set to 100 to test the ungraceful shutdown
        await sleep.defer_async(length=5)

        print("STARTUP")
        yield
        print("SHUTDOWN")

        worker.cancel()
        try:
            await asyncio.wait_for(worker, timeout=10)
        except asyncio.TimeoutError:
            print("Ungraceful shutdown")
        except asyncio.CancelledError:
            print("Graceful shutdown")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"Hello": "World"}
```
