from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.13.00_01_pre_add_retry_job_v3.sql"
        ),
    ]
    name = "0048_pre_add_retry_job_v3"
    dependencies = [
        ("procrastinate", "0047_post_drop_id_lock_index"),
    ]
