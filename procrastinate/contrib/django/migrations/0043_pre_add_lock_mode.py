from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(name="03.12.00_01_pre_add_lock_mode.sql"),
    ]
    name = "0043_pre_add_lock_mode"
    dependencies = [
        ("procrastinate", "0042_pre_fetch_job_skip_null_lock"),
    ]
