from __future__ import annotations

from django.db import migrations, models

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.10.00_01_pre_add_deferred_at.sql"
        ),
        migrations.AddField(
            "procrastinatejob",
            "deferred_at",
            models.DateTimeField(blank=True, null=True),
        ),
    ]
    name = "0042_pre_add_deferred_at"
    dependencies = [
        ("procrastinate", "0041_post_retry_failed_job"),
    ]
