from django.db import migrations

from procrastinate.schema import get_sql


class Migration(migrations.Migration):

    dependencies = [("procrastinate", "0009_add_defer_job_function")]

    operations = [
        migrations.RunSQL(
            get_sql("delta_0.11.0_003_add_procrastinate_periodic_defers.sql")
        ),
    ]
