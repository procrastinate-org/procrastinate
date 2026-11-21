from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.13.00_50_post_drop_retry_job_v2.sql"
        ),
    ]
    name = "0049_post_drop_retry_job_v2"
    dependencies = [
        ("procrastinate", "0048_pre_add_retry_job_v3"),
    ]
