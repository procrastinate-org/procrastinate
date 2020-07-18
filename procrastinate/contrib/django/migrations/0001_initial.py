from django.db import migrations

from ..utils import get_sql


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.RunSQL(get_sql("baseline-0.5.0.sql")),
    ]
