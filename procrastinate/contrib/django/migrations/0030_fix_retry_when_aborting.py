from __future__ import annotations

from django.db import migrations

from .. import migrations_utils


class Migration(migrations.Migration):
    operations = [
        migrations_utils.RunProcrastinateSQL(
            name="02.09.01_01_fix_retry_when_aborting.sql"
        ),
    ]
    name = "0030_fix_retry_when_aborting"
    dependencies = [("procrastinate", "0029_add_additional_params_to_retry_job")]
