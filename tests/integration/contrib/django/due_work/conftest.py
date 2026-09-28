from __future__ import annotations

try:
    from due_work_harness import configure
    from due_work_harness.integrations.django import django_host
except ImportError:  # due-work-harness needs Python 3.12+
    collect_ignore_glob = ["test_*.py"]
else:
    # The system under test is procrastinate, running on Django: every binding
    # must reach one of them. Configured here, so only this directory uses it.
    configure(
        django_host(
            production_packages={"procrastinate", "django"}, lifecycle_proofs=False
        )
    )
