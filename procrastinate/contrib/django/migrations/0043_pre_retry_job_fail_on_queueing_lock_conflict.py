from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.12.00_01_pre_retry_job_fail_on_queueing_lock_conflict.sql"
        ),
    ]
    name = "0043_pre_retry_job_fail_on_queueing_lock_conflict"
    dependencies = [
        ("procrastinate", "0042_pre_fetch_job_skip_null_lock"),
    ]
