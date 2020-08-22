from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = False
    dependencies: list = [("procrastinate", "0006_fix_trigger_status_events_insert")]
    operations = [
        migrations.RunSQL(
            schema.get_sql("delta_0.8.1_001_add_queueing_lock_column.sql")
        )
    ]
