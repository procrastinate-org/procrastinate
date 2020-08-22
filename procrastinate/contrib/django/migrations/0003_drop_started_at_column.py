from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = False
    dependencies: list = [("procrastinate", "0002_drop_started_at_column")]
    operations = [
        migrations.RunSQL(schema.get_sql("delta_0.5.0_001_drop_started_at_column.sql"))
    ]
