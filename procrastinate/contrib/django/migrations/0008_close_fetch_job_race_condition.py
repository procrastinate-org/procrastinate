from django.db import migrations

from procrastinate.schema import get_sql


class Migration(migrations.Migration):

    dependencies = [("procrastinate", "0007_add_queueing_lock_column")]

    operations = [
        migrations.RunSQL(
            get_sql("delta_0.10.0_001_close_fetch_job_race_condition.sql")
        ),
    ]
