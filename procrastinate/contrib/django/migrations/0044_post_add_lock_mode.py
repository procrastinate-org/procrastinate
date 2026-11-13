from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(name="03.12.00_50_post_add_lock_mode.sql"),
    ]
    name = "0044_post_add_lock_mode"
    dependencies = [
        ("procrastinate", "0043_pre_add_lock_mode"),
    ]
