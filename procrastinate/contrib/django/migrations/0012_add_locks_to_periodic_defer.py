from django.db import migrations

from procrastinate.schema import get_sql


class Migration(migrations.Migration):

    dependencies = [("procrastinate", "0011_add_foreign_key_index")]

    operations = [
        migrations.RunSQL(get_sql("delta_0.14.0_001_add_locks_to_periodic_defer.sql")),
    ]
