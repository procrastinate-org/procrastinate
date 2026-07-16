from __future__ import annotations

from django.db import migrations, models

import procrastinate.contrib.django.models


class Migration(migrations.Migration):
    operations = [
        migrations.CreateModel(
            name="ProcrastinatePausedQueue",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("queue_name", models.CharField(max_length=128)),
                ("pause_key", models.CharField(max_length=128)),
                ("paused_at", models.DateTimeField()),
            ],
            options={
                "db_table": "procrastinate_paused_queues",
                "managed": False,
            },
            bases=(
                procrastinate.contrib.django.models.ProcrastinateReadOnlyModelMixin,
                models.Model,
            ),
        ),
    ]
    name = "0044_add_paused_queue_model"
    dependencies = [
        ("procrastinate", "0043_post_add_queue_pause"),
    ]
