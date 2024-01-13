# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/procrastinate-org/procrastinate/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| procrastinate/\_\_init\_\_.py                           |       18 |        0 |        0 |        0 |    100% |           |
| procrastinate/\_\_main\_\_.py                           |        5 |        0 |        2 |        0 |    100% |           |
| procrastinate/app.py                                    |       80 |        1 |       10 |        0 |     99% |       264 |
| procrastinate/blueprints.py                             |       50 |        0 |       14 |        0 |    100% |           |
| procrastinate/builtin\_tasks.py                         |        7 |        0 |        2 |        0 |    100% |           |
| procrastinate/cli.py                                    |      176 |        2 |       32 |        1 |     99% |    11, 51 |
| procrastinate/connector.py                              |       39 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/aiopg/\_\_init\_\_.py             |        2 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/aiopg/aiopg\_connector.py         |      152 |        2 |       92 |        2 |     98% |207-208, 306->305 |
| procrastinate/contrib/django/\_\_init\_\_.py            |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/apps.py                    |        7 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/migrations\_magic.py       |       72 |        0 |       29 |        0 |    100% |           |
| procrastinate/contrib/django/utils.py                   |        5 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/psycopg2/\_\_init\_\_.py          |        2 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/psycopg2/psycopg2\_connector.py   |      104 |        1 |       64 |        1 |     99% |        26 |
| procrastinate/contrib/sqlalchemy/\_\_init\_\_.py        |        2 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/sqlalchemy/psycopg2\_connector.py |       81 |        1 |       50 |        0 |     99% |       120 |
| procrastinate/exceptions.py                             |       35 |        0 |        2 |        0 |    100% |           |
| procrastinate/job\_context.py                           |       52 |        0 |       20 |        0 |    100% |           |
| procrastinate/jobs.py                                   |       72 |        0 |       12 |        0 |    100% |           |
| procrastinate/manager.py                                |       97 |        0 |       30 |        0 |    100% |           |
| procrastinate/metadata.py                               |        5 |        0 |        0 |        0 |    100% |           |
| procrastinate/periodic.py                               |       95 |        1 |       26 |        1 |     98% |        23 |
| procrastinate/psycopg\_connector.py                     |      115 |        5 |       66 |        4 |     95% |164-166, 239, 265->264, 298 |
| procrastinate/retry.py                                  |       37 |        0 |       14 |        0 |    100% |           |
| procrastinate/schema.py                                 |       21 |        0 |        4 |        0 |    100% |           |
| procrastinate/shell.py                                  |       60 |        5 |       16 |        0 |     93% |     41-45 |
| procrastinate/signals.py                                |       43 |        0 |       10 |        0 |    100% |           |
| procrastinate/sql/\_\_init\_\_.py                       |       20 |        0 |        0 |        0 |    100% |           |
| procrastinate/sql/migrations/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/sync\_psycopg\_connector.py               |       87 |        3 |       48 |        3 |     96% |33, 151, 176 |
| procrastinate/tasks.py                                  |       47 |        0 |       12 |        0 |    100% |           |
| procrastinate/testing.py                                |      141 |        1 |       63 |        1 |     99% |       146 |
| procrastinate/types.py                                  |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/utils.py                                  |      188 |        4 |       62 |        4 |     95% |261-262, 327->318, 344->336, 362-363 |
| procrastinate/worker.py                                 |      164 |        0 |       42 |        0 |    100% |           |
|                                               **TOTAL** | **2087** |   **26** |  **722** |   **17** | **98%** |           |


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