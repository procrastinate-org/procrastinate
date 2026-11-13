from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.12.00_02_pre_retry_job_fail_on_queueing_lock_conflict.sql"
        ),
    ]
    name = "0045_pre_retry_job_fail_on_queueing_lock_conflict"
    dependencies = [
        ("procrastinate", "0044_post_add_lock_mode"),
    ]
