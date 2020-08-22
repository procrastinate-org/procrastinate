from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = False
    dependencies: list = [("procrastinate", "0003_drop_started_at_column")]
    operations = [
        migrations.RunSQL(
            schema.get_sql("delta_0.5.0_003_drop_procrastinate_version_table.sql")
        )
    ]
