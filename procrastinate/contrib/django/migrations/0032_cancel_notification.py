from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="03.00.00_01_cancel_notification.sql"
        ),
    ]
    name = "0032_cancel_notification"
    dependencies = [("procrastinate", "0031_add_abort_on_procrastinate_jobs")]
