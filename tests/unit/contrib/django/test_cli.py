from __future__ import annotations

import argparse

from procrastinate.contrib.django.management.commands import (
    procrastinate as procrastinate_command,
)


def test_procrastinate_command():
    # This test might be brittle as it uses internal argparse attributes
    # It's linked to https://github.com/procrastinate-org/procrastinate/pull/1095
    parser = procrastinate_command.Command().create_parser("manage.py", "procrastinate")

    error = """
    If this test fails, it means that an argument named "args" has been added
    (or renamed) in the procrastinate CLI, and is exposed in the Django procrastinate
    management command. This is problematic because "args" is a special name that
    Django removes from the command line arguments before passing them to the
    management command. To fix this error, use a different name for the argument.

    See:
        - https://github.com/django/django/blob/f9bf616597d56deac66d9d6bb753b028dd9634cc/django/core/management/base.py#L410
        - https://github.com/procrastinate-org/procrastinate/pull/1095
    """

    def assert_no_action_named_args(parser):
        for action in parser._actions:
            assert getattr(action, "dest", "") != ("args"), (
                f"'args' found in {parser.prog}\n{error}"
            )
            if isinstance(action, argparse._SubParsersAction):
                for subparser in action.choices.values():
                    assert_no_action_named_args(subparser)

    assert_no_action_named_args(parser)
