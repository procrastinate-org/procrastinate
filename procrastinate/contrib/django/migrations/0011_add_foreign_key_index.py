from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = False
    dependencies: list = [("procrastinate", "0010_add_procrastinate_periodic_defers")]
    operations = [
        migrations.RunSQL(schema.get_sql("delta_0.12.0_001_add_foreign_key_index.sql"))
    ]
