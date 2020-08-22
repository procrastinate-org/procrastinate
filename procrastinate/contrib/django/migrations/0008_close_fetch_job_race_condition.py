from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = False
    dependencies: list = [("procrastinate", "0007_add_queueing_lock_column")]
    operations = [
        migrations.RunSQL(
            schema.get_sql("delta_0.10.0_001_close_fetch_job_race_condition.sql")
        )
    ]
