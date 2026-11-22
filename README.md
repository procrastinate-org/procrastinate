# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/procrastinate-org/procrastinate/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                                               |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------------------------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| procrastinate/\_\_init\_\_.py                                                                                      |       19 |        0 |        0 |        0 |    100% |           |
| procrastinate/\_\_main\_\_.py                                                                                      |        6 |        0 |        2 |        0 |    100% |           |
| procrastinate/app.py                                                                                               |      109 |        0 |        4 |        0 |    100% |           |
| procrastinate/blueprints.py                                                                                        |       64 |        0 |       14 |        0 |    100% |           |
| procrastinate/builtin\_tasks.py                                                                                    |        6 |        0 |        0 |        0 |    100% |           |
| procrastinate/cli.py                                                                                               |      240 |       10 |       42 |        1 |     94% |86, 175-181, 762-765 |
| procrastinate/connector.py                                                                                         |       54 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/\_\_init\_\_.py                                                                              |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/aiopg/\_\_init\_\_.py                                                                        |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/aiopg/aiopg\_connector.py                                                                    |      160 |        2 |       38 |        1 |     98% |   205-206 |
| procrastinate/contrib/alembic/\_\_init\_\_.py                                                                      |        1 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/alembic/migrations\_utils.py                                                                 |       24 |        1 |        4 |        1 |     93% |        25 |
| procrastinate/contrib/alembic/versions/\_\_init\_\_.py                                                             |        1 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/alembic/versions/procrastinate\_0000\_initial.py                                             |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0001\_drop\_started\_at\_column.py                           |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0002\_drop\_started\_at\_column.py                           |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0003\_drop\_procrastinate\_version\_table.py                 |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0004\_fix\_procrastinate\_fetch\_job.py                      |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0005\_fix\_trigger\_status\_events\_insert.py                |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0006\_add\_queueing\_lock\_column.py                         |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0007\_close\_fetch\_job\_race\_condition.py                  |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0008\_add\_defer\_job\_function.py                           |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0009\_add\_procrastinate\_periodic\_defers.py                |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0010\_add\_foreign\_key\_index.py                            |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0011\_add\_locks\_to\_periodic\_defer.py                     |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0012\_fix\_procrastinate\_defer\_periodic\_job.py            |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0013\_add\_finish\_job\_and\_retry\_job\_functions.py        |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0014\_add\_trigger\_on\_job\_deletion.py                     |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0015\_delete\_finished\_jobs.py                              |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0016\_add\_checks\_to\_finish\_job.py                        |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0017\_add\_checks\_to\_retry\_job.py                         |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0018\_fix\_finish\_job\_compat\_issue.py                     |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0019\_add\_index\_on\_procrastinate\_jobs.py                 |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0020\_add\_kwargs\_to\_defer\_periodic\_job.py               |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0021\_null\_locks\_excluded.py                               |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0022\_remove\_old\_finish\_job\_function.py                  |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0023\_job\_id\_bigint.py                                     |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0024\_add\_job\_priority.py                                  |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0025\_add\_periodic\_job\_priority.py                        |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0026\_add\_cancel\_states.py                                 |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0027\_add\_additional\_params\_to\_retry\_job.py             |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0028\_add\_indexes\_for\_fetch\_job.py                       |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0029\_pre\_cancel\_notification.py                           |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0030\_post\_cancel\_notification.py                          |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0031\_pre\_add\_heartbeat.py                                 |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0032\_post\_add\_heartbeat.py                                |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0033\_pre\_batch\_defer\_jobs.py                             |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0034\_post\_batch\_defer\_jobs.py                            |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0035\_pre\_priority\_lock\_fetch\_job.py                     |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0036\_pre\_add\_retry\_failed\_job\_procedure.py             |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0037\_post\_add\_retry\_failed\_job\_procedure.py            |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0038\_pre\_fetch\_job\_skip\_null\_lock.py                   |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0039\_pre\_add\_lock\_mode.py                                |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0040\_pre\_retry\_job\_fail\_on\_queueing\_lock\_conflict.py |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0041\_pre\_add\_todo\_doing\_lock\_index.py                  |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0042\_post\_add\_lock\_mode.py                               |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0043\_post\_drop\_id\_lock\_index.py                         |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0044\_pre\_add\_retry\_job\_v3.py                            |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/alembic/versions/procrastinate\_0045\_post\_drop\_retry\_job\_v2.py                          |       11 |        1 |        0 |        0 |     91% |        20 |
| procrastinate/contrib/django/\_\_init\_\_.py                                                                       |        5 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/apps.py                                                                               |       29 |        1 |        6 |        0 |     97% |        24 |
| procrastinate/contrib/django/db\_cleanup.py                                                                        |       30 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/django\_connector.py                                                                  |       89 |        4 |       18 |        1 |     95% | 27-30, 38 |
| procrastinate/contrib/django/exceptions.py                                                                         |        6 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/healthchecks.py                                                                       |       32 |        0 |        2 |        0 |    100% |           |
| procrastinate/contrib/django/management/\_\_init\_\_.py                                                            |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/management/commands/\_\_init\_\_.py                                                   |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/management/commands/procrastinate.py                                                  |       29 |        3 |        6 |        2 |     80% |33-36, 41-\>45 |
| procrastinate/contrib/django/migrations\_utils.py                                                                  |       11 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/models.py                                                                             |       81 |        4 |        6 |        1 |     94% |33, 74, 132, 160 |
| procrastinate/contrib/django/procrastinate\_app.py                                                                 |       21 |        1 |        2 |        0 |     96% |        58 |
| procrastinate/contrib/django/settings.py                                                                           |       18 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/utils.py                                                                              |       16 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/psycopg2/\_\_init\_\_.py                                                                     |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/psycopg2/psycopg2\_connector.py                                                              |      108 |        0 |       14 |        0 |    100% |           |
| procrastinate/contrib/sphinx/\_\_init\_\_.py                                                                       |       17 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/sqlalchemy/\_\_init\_\_.py                                                                   |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/sqlalchemy/psycopg2\_connector.py                                                            |      100 |        2 |       16 |        0 |     98% |     31-32 |
| procrastinate/demos/\_\_init\_\_.py                                                                                |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_async/\_\_init\_\_.py                                                                    |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_async/\_\_main\_\_.py                                                                    |       31 |       31 |        6 |        0 |      0% |      1-42 |
| procrastinate/demos/demo\_async/app.py                                                                             |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_async/tasks.py                                                                           |        8 |        2 |        0 |        0 |     75% |     9, 15 |
| procrastinate/demos/demo\_django/\_\_init\_\_.py                                                                   |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_django/\_\_main\_\_.py                                                                   |        4 |        4 |        2 |        0 |      0% |       1-6 |
| procrastinate/demos/demo\_django/demo/\_\_init\_\_.py                                                              |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_django/demo/admin.py                                                                     |        4 |        4 |        0 |        0 |      0% |       1-7 |
| procrastinate/demos/demo\_django/demo/apps.py                                                                      |        4 |        4 |        0 |        0 |      0% |       1-7 |
| procrastinate/demos/demo\_django/demo/migrations/0001\_initial.py                                                  |        6 |        6 |        0 |        0 |      0% |      2-12 |
| procrastinate/demos/demo\_django/demo/migrations/\_\_init\_\_.py                                                   |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_django/demo/models.py                                                                    |        8 |        8 |        0 |        0 |      0% |      1-12 |
| procrastinate/demos/demo\_django/demo/tasks.py                                                                     |       18 |       18 |        0 |        0 |      0% |      1-34 |
| procrastinate/demos/demo\_django/demo/views.py                                                                     |       14 |       14 |        0 |        0 |      0% |      1-22 |
| procrastinate/demos/demo\_django/manage.py                                                                         |       12 |       12 |        2 |        0 |      0% |      4-27 |
| procrastinate/demos/demo\_django/project/\_\_init\_\_.py                                                           |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_django/project/asgi.py                                                                   |        5 |        5 |        0 |        0 |      0% |     10-20 |
| procrastinate/demos/demo\_django/project/settings.py                                                               |       30 |       30 |        4 |        0 |      0% |    13-202 |
| procrastinate/demos/demo\_django/project/urls.py                                                                   |        6 |        6 |        0 |        0 |      0% |     18-26 |
| procrastinate/demos/demo\_django/project/wsgi.py                                                                   |        5 |        5 |        0 |        0 |      0% |     10-20 |
| procrastinate/demos/demo\_sync/\_\_init\_\_.py                                                                     |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_sync/\_\_main\_\_.py                                                                     |       28 |       28 |        6 |        0 |      0% |      1-37 |
| procrastinate/demos/demo\_sync/app.py                                                                              |        3 |        3 |        0 |        0 |      0% |       1-5 |
| procrastinate/demos/demo\_sync/tasks.py                                                                            |        8 |        8 |        0 |        0 |      0% |      1-13 |
| procrastinate/exceptions.py                                                                                        |       39 |        0 |        2 |        0 |    100% |           |
| procrastinate/job\_context.py                                                                                      |       43 |        1 |        2 |        0 |     98% |        84 |
| procrastinate/jobs.py                                                                                              |      123 |        0 |       10 |        0 |    100% |           |
| procrastinate/manager.py                                                                                           |      179 |        0 |       44 |        0 |    100% |           |
| procrastinate/metadata.py                                                                                          |        6 |        0 |        0 |        0 |    100% |           |
| procrastinate/middleware.py                                                                                        |       27 |        2 |        6 |        0 |     94% |     53-54 |
| procrastinate/periodic.py                                                                                          |      114 |        0 |       22 |        0 |    100% |           |
| procrastinate/psycopg\_connector.py                                                                                |      154 |       10 |       40 |        4 |     93% |43-44, 148-150, 240, 265, 337-338, 388 |
| procrastinate/retry.py                                                                                             |       66 |        0 |       18 |        1 |     99% |   77-\>80 |
| procrastinate/schema.py                                                                                            |       24 |        0 |        0 |        0 |    100% |           |
| procrastinate/shell.py                                                                                             |       61 |        3 |       12 |        0 |     96% |     45-47 |
| procrastinate/signals.py                                                                                           |       50 |        3 |       10 |        1 |     93% |     31-36 |
| procrastinate/sql/\_\_init\_\_.py                                                                                  |       20 |        0 |        0 |        0 |    100% |           |
| procrastinate/sql/migrations/\_\_init\_\_.py                                                                       |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/sync\_psycopg\_connector.py                                                                          |      101 |        3 |       22 |        3 |     95% |160, 185, 207 |
| procrastinate/tasks.py                                                                                             |       95 |        0 |       14 |        0 |    100% |           |
| procrastinate/testing.py                                                                                           |      255 |       10 |       72 |        2 |     96% |95, 105, 306-318, 566-\>565 |
| procrastinate/types.py                                                                                             |       22 |        0 |        0 |        0 |    100% |           |
| procrastinate/utils.py                                                                                             |      191 |        0 |       48 |        0 |    100% |           |
| procrastinate/worker.py                                                                                            |      335 |       10 |      106 |        8 |     96% |91, 108, 234-\>237, 522-\>exit, 543-544, 548-549, 585, 696-\>exit, 702, 718-727 |
| **TOTAL**                                                                                                          | **3893** |  **304** |  **622** |   **26** | **92%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/procrastinate-org/procrastinate/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/procrastinate-org/procrastinate/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/procrastinate-org/procrastinate/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/procrastinate-org/procrastinate/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fprocrastinate-org%2Fprocrastinate%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/procrastinate-org/procrastinate/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.