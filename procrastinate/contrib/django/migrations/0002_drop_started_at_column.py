from django.db import migrations

from procrastinate.contrib.django.utils import get_sql


class Migration(migrations.Migration):

    dependencies = [("procrastinate_django", "0001_initial")]

    operations = [
        migrations.RunSQL(get_sql("delta_0.5.0_001_drop_started_at_column.sql")),
    ]
