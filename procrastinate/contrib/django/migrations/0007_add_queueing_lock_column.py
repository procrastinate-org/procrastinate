from django.db import migrations

from procrastinate.schema import get_sql


class Migration(migrations.Migration):

    dependencies = [("procrastinate", "0006_fix_trigger_status_events_insert")]

    operations = [
        migrations.RunSQL(get_sql("delta_0.8.1_001_add_queueing_lock_column.sql")),
    ]
