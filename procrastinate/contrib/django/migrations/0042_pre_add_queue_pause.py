from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.10.00_01_pre_add_queue_pause.sql"
        ),
    ]
    name = "0042_pre_add_queue_pause"
    dependencies = [
        ("procrastinate", "0041_post_retry_failed_job"),
    ]
