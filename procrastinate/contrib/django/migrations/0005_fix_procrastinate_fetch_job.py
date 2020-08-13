from django.db import migrations

from procrastinate.schema import get_sql


class Migration(migrations.Migration):

    dependencies = [("procrastinate_django", "0004_drop_procrastinate_version_table")]

    operations = [
        migrations.RunSQL(get_sql("delta_0.6.0_001_fix_procrastinate_fetch_job.sql")),
    ]
