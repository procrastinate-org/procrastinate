from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = False
    dependencies: list = [("procrastinate", "0005_fix_procrastinate_fetch_job")]
    operations = [
        migrations.RunSQL(
            schema.get_sql("delta_0.7.1_001_fix_trigger_status_events_insert.sql")
        )
    ]
