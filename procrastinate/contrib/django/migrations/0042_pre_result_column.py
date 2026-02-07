from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.08.00_01_pre_result_to_job_procedure.sql"
        ),
    ]
    name = "0042_pre_result_column"
    dependencies = [
        ("procrastinate", "0041_post_retry_failed_job"),
    ]
