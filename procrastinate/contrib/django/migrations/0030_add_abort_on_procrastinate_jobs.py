from __future__ import annotations

from django.db import migrations, models

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="02.09.02_01_add_abort_on_procrastinate_jobs.sql"
        ),
        migrations.AlterField(
            "procrastinatejob",
            "status",
            models.CharField(
                choices=[
                    ("todo", "todo"),
                    ("doing", "doing"),
                    ("succeeded", "succeeded"),
                    ("failed", "failed"),
                    ("cancelled", "cancelled"),
                    ("aborted", "aborted"),
                ],
                max_length=32,
            ),
        ),
        migrations.AddField(
            "procrastinatejob",
            "abort",
            models.BooleanField(),
        ),
    ]
    name = "0030_add_abort_on_procrastinate_jobs"
    dependencies = [("procrastinate", "0029_add_additional_params_to_retry_job")]
