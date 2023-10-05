# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/procrastinate-org/procrastinate/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| procrastinate/\_\_init\_\_.py                           |       15 |        0 |        0 |        0 |    100% |           |
| procrastinate/\_\_main\_\_.py                           |        5 |        0 |        2 |        0 |    100% |           |
| procrastinate/aiopg\_connector.py                       |      145 |        0 |       90 |        1 |     99% |  309->308 |
| procrastinate/app.py                                    |       74 |        0 |        8 |        0 |    100% |           |
| procrastinate/blueprints.py                             |       50 |        0 |       14 |        0 |    100% |           |
| procrastinate/builtin\_tasks.py                         |        7 |        0 |        2 |        0 |    100% |           |
| procrastinate/cli.py                                    |      182 |        1 |      137 |        1 |     99% |        13 |
| procrastinate/connector.py                              |       38 |        0 |        2 |        0 |    100% |           |
| procrastinate/contrib/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/\_\_init\_\_.py            |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/apps.py                    |        7 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/django/migrations\_magic.py       |       72 |        0 |       29 |        0 |    100% |           |
| procrastinate/contrib/django/utils.py                   |        5 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/sqlalchemy/\_\_init\_\_.py        |        2 |        0 |        0 |        0 |    100% |           |
| procrastinate/contrib/sqlalchemy/psycopg2\_connector.py |       79 |        0 |       50 |        0 |    100% |           |
| procrastinate/exceptions.py                             |       28 |        0 |        2 |        0 |    100% |           |
| procrastinate/job\_context.py                           |       52 |        0 |       20 |        0 |    100% |           |
| procrastinate/jobs.py                                   |       72 |        0 |       12 |        0 |    100% |           |
| procrastinate/manager.py                                |       86 |        0 |       22 |        0 |    100% |           |
| procrastinate/metadata.py                               |        5 |        0 |        0 |        0 |    100% |           |
| procrastinate/periodic.py                               |       95 |        1 |       26 |        1 |     98% |        23 |
| procrastinate/psycopg2\_connector.py                    |      104 |        0 |       64 |        0 |    100% |           |
| procrastinate/retry.py                                  |       37 |        0 |       14 |        0 |    100% |           |
| procrastinate/schema.py                                 |       19 |        0 |        4 |        0 |    100% |           |
| procrastinate/shell.py                                  |       49 |        0 |       14 |        0 |    100% |           |
| procrastinate/signals.py                                |       43 |        0 |       10 |        0 |    100% |           |
| procrastinate/sql/\_\_init\_\_.py                       |       19 |        0 |        0 |        0 |    100% |           |
| procrastinate/sql/migrations/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| procrastinate/tasks.py                                  |       47 |        0 |       12 |        0 |    100% |           |
| procrastinate/testing.py                                |      133 |        0 |       63 |        0 |    100% |           |
| procrastinate/types.py                                  |        3 |        0 |        0 |        0 |    100% |           |
| procrastinate/utils.py                                  |      206 |        4 |       80 |        4 |     96% |353-354, 419->410, 436->428, 454-455 |
| procrastinate/worker.py                                 |      154 |        0 |       40 |        0 |    100% |           |
|                                               **TOTAL** | **1836** |    **6** |  **717** |    **7** | **99%** |           |


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