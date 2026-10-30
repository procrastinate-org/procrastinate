from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.11.00_01_pre_fence_job_reports.sql"
        ),
    ]
    name = "0042_pre_fence_job_reports"
    dependencies = [
        ("procrastinate", "0041_post_retry_failed_job"),
    ]
