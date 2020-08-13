from django.db import migrations

from procrastinate.schema import get_sql


class Migration(migrations.Migration):

    dependencies = [("procrastinate_django", "0010_add_procrastinate_periodic_defers")]

    operations = [
        migrations.RunSQL(get_sql("delta_0.12.0_001_add_foreign_key_index.sql")),
    ]
