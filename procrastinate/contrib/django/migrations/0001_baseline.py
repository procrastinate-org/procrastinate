from django.db import migrations

from procrastinate import schema


class Migration(migrations.Migration):
    initial = True
    dependencies: list = []
    operations = [migrations.RunSQL(schema.get_sql("baseline-0.5.0.sql"))]
