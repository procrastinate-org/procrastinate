# Running on Windows

Procrastinate has been tested and is known to work on Windows. However, there are
a few things to keep in mind:

-  Due to the way signals are implemented on Windows (in short, they are not fully supported),
  the worker will not be able to gracefully stop when receiving a `SIGINT` or `SIGTERM` signal
  as described in the {doc}`../production/retry_stalled_jobs` guide. This means that any running
  jobs will be halted abruptly.

- We do not use windows for running Procrastinate in production, so we may not
  be aware of all the issues that may arise.

Given these limitations, we strongly advise using a Unix-like system for running Procrastinate
in production. Windows should primarily be used for development purposes only.
