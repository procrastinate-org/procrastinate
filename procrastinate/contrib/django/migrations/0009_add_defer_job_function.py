from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = False
    dependencies: list = [("procrastinate", "0008_close_fetch_job_race_condition")]
    operations = [
        migrations.RunSQL(schema.get_sql("delta_0.10.0_002_add_defer_job_function.sql"))
    ]
