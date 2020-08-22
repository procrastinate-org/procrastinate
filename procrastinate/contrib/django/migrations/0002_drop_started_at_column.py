from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = False
    dependencies: list = [("procrastinate", "0001_baseline")]
    operations = [
        migrations.RunSQL(schema.get_sql("delta_0.5.0_002_drop_started_at_column.sql"))
    ]
