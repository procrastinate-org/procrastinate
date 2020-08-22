from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = False
    dependencies: list = [("procrastinate", "0004_drop_procrastinate_version_table")]
    operations = [
        migrations.RunSQL(
            schema.get_sql("delta_0.6.0_001_fix_procrastinate_fetch_job.sql")
        )
    ]
