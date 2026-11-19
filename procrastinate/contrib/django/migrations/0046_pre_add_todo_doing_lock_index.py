from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    atomic = False
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.12.00_03_pre_add_todo_doing_lock_index.sql"
        ),
    ]
    name = "0046_pre_add_todo_doing_lock_index"
    dependencies = [
        ("procrastinate", "0045_pre_retry_job_fail_on_queueing_lock_conflict"),
    ]
