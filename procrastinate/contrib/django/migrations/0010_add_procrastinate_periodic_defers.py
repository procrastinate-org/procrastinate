from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = False
    dependencies: list = [("procrastinate", "0009_add_defer_job_function")]
    operations = [
        migrations.RunSQL(
            schema.get_sql("delta_0.11.0_003_add_procrastinate_periodic_defers.sql")
        )
    ]
