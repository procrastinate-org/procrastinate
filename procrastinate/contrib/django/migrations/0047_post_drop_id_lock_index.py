from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    atomic = False
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.12.00_51_post_drop_id_lock_index.sql"
        ),
    ]
    name = "0047_post_drop_id_lock_index"
    dependencies = [
        ("procrastinate", "0046_pre_add_todo_doing_lock_index"),
    ]
