# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/procrastinate-org/procrastinate/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                              |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------------------------------------ | -------: | -------: | -------: | -------: | ------: | --------: |
| procrastinate/\_\_init\_\_.py                                     |       19 |        0 |        0 |        0 |    100% |           |
| procrastinate/\_\_main\_\_.py                                     |        6 |        0 |        2 |        0 |    100% |           |
| procrastinate/app.py                                              |      104 |        0 |        2 |        0 |    100% |           |
| procrastinate/blueprints.py                                       |       68 |        0 |       14 |        0 |    100% |           |
| procrastinate/builtin\_tasks.py                                   |        6 |        0 |        0 |        0 |    100% |           |
| procrastinate/cli.py                                              |      223 |        4 |       34 |        3 |     97% |50, 137, 141, 679 |
| procrastinate/connector.py                                        |       43 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/\_\_init\_\_.py                             |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/aiopg/\_\_init\_\_.py                       |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/aiopg/aiopg\_connector.py                   |      167 |        2 |       40 |        1 |     99% |   215-216 |
| procrastinate/contrib/django/\_\_init\_\_.py                      |        4 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/apps.py                              |       29 |        1 |        6 |        0 |     97% |        24 |
| procrastinate/contrib/django/django\_connector.py                 |       92 |        4 |       18 |        1 |     95% | 27-30, 38 |
| procrastinate/contrib/django/exceptions.py                        |        6 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/healthchecks.py                      |       32 |        0 |        2 |        0 |    100% |           |
| procrastinate/contrib/django/management/\_\_init\_\_.py           |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/management/commands/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/management/commands/procrastinate.py |       23 |        1 |        4 |        2 |     89% |29, 34->38 |
| procrastinate/contrib/django/migrations\_utils.py                 |       11 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/models.py                            |       79 |        4 |        6 |        1 |     94% |33, 74, 124, 152 |
| procrastinate/contrib/django/procrastinate\_app.py                |       21 |        1 |        2 |        0 |     96% |        58 |
| procrastinate/contrib/django/settings.py                          |       18 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/utils.py                             |       16 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/psycopg2/\_\_init\_\_.py                    |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/psycopg2/psycopg2\_connector.py             |      120 |        0 |       16 |        1 |     99% |    30->37 |
| procrastinate/contrib/sphinx/\_\_init\_\_.py                      |       16 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/sqlalchemy/\_\_init\_\_.py                  |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/sqlalchemy/psycopg2\_connector.py           |       99 |        5 |       18 |        2 |     94% |40-41, 123, 153, 155 |
| procrastinate/demos/\_\_init\_\_.py                               |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_async/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_async/\_\_main\_\_.py                   |       30 |       30 |        6 |        0 |      0% |      1-40 |
| procrastinate/demos/demo\_async/app.py                            |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_async/tasks.py                          |        8 |        2 |        0 |        0 |     75% |     9, 15 |
| procrastinate/demos/demo\_django/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_django/\_\_main\_\_.py                  |        4 |        4 |        2 |        0 |      0% |       1-6 |
| procrastinate/demos/demo\_django/demo/\_\_init\_\_.py             |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_django/demo/admin.py                    |        4 |        4 |        0 |        0 |      0% |       1-7 |
| procrastinate/demos/demo\_django/demo/apps.py                     |        4 |        4 |        0 |        0 |      0% |       1-7 |
| procrastinate/demos/demo\_django/demo/migrations/0001\_initial.py |        6 |        6 |        0 |        0 |      0% |      2-12 |
| procrastinate/demos/demo\_django/demo/migrations/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_django/demo/models.py                   |        8 |        8 |        0 |        0 |      0% |      1-12 |
| procrastinate/demos/demo\_django/demo/tasks.py                    |       18 |       18 |        0 |        0 |      0% |      1-34 |
| procrastinate/demos/demo\_django/demo/views.py                    |       13 |       13 |        0 |        0 |      0% |      1-20 |
| procrastinate/demos/demo\_django/manage.py                        |       12 |       12 |        2 |        0 |      0% |      4-27 |
| procrastinate/demos/demo\_django/project/\_\_init\_\_.py          |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_django/project/asgi.py                  |        5 |        5 |        0 |        0 |      0% |     10-20 |
| procrastinate/demos/demo\_django/project/settings.py              |       30 |       30 |        4 |        0 |      0% |    13-181 |
| procrastinate/demos/demo\_django/project/urls.py                  |        6 |        6 |        0 |        0 |      0% |     18-26 |
| procrastinate/demos/demo\_django/project/wsgi.py                  |        5 |        5 |        0 |        0 |      0% |     10-20 |
| procrastinate/demos/demo\_sync/\_\_init\_\_.py                    |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/demos/demo\_sync/\_\_main\_\_.py                    |       27 |       27 |        6 |        0 |      0% |      1-35 |
| procrastinate/demos/demo\_sync/app.py                             |        3 |        3 |        0 |        0 |      0% |       1-5 |
| procrastinate/demos/demo\_sync/tasks.py                           |        8 |        8 |        0 |        0 |      0% |      1-13 |
| procrastinate/exceptions.py                                       |       32 |        0 |        2 |        0 |    100% |           |
| procrastinate/job\_context.py                                     |       43 |        1 |        2 |        0 |     98% |        84 |
| procrastinate/jobs.py                                             |      114 |        0 |        8 |        0 |    100% |           |
| procrastinate/manager.py                                          |      149 |        0 |       24 |        0 |    100% |           |
| procrastinate/metadata.py                                         |        6 |        0 |        0 |        0 |    100% |           |
| procrastinate/periodic.py                                         |      105 |        0 |       20 |        0 |    100% |           |
| procrastinate/psycopg\_connector.py                               |      117 |        5 |       32 |        3 |     95% |135-137, 219, 291 |
| procrastinate/retry.py                                            |       66 |        0 |       18 |        1 |     99% |    77->80 |
| procrastinate/schema.py                                           |       25 |        0 |        0 |        0 |    100% |           |
| procrastinate/shell.py                                            |       61 |        3 |       12 |        0 |     96% |     45-47 |
| procrastinate/signals.py                                          |       49 |        3 |       10 |        1 |     93% |     30-35 |
| procrastinate/sql/\_\_init\_\_.py                                 |       21 |        0 |        0 |        0 |    100% |           |
| procrastinate/sql/migrations/\_\_init\_\_.py                      |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/sync\_psycopg\_connector.py                         |       98 |        2 |       22 |        3 |     96% |33->40, 162, 187 |
| procrastinate/tasks.py                                            |       75 |        0 |        8 |        0 |    100% |           |
| procrastinate/testing.py                                          |      225 |        7 |       60 |        2 |     96% |251-260, 474->473 |
| procrastinate/types.py                                            |       22 |        0 |        0 |        0 |    100% |           |
| procrastinate/utils.py                                            |      165 |        0 |       36 |        0 |    100% |           |
| procrastinate/worker.py                                           |      253 |        7 |       72 |        7 |     96% |72, 86, 196->199, 406->exit, 427-428, 432-433, 449->448, 466 |
|                                                         **TOTAL** | **3031** |  **235** |  **510** |   **28** | **92%** |           |


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