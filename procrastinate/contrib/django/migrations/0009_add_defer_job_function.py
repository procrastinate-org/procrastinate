from django.db import migrations

from procrastinate.schema import get_sql


class Migration(migrations.Migration):

    dependencies = [("procrastinate", "0008_close_fetch_job_race_condition")]

    operations = [
        migrations.RunSQL(get_sql("delta_0.10.0_002_add_defer_job_function.sql")),
    ]
