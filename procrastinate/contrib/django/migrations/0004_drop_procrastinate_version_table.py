from django.db import migrations

from procrastinate.schema import get_sql


class Migration(migrations.Migration):

    dependencies = [("procrastinate", "0003_drop_started_at_column")]

    operations = [
        migrations.RunSQL(
            get_sql("delta_0.5.0_003_drop_procrastinate_version_table.sql")
        ),
    ]
