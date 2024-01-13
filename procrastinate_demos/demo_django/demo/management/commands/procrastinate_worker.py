from __future__ import annotations

from django.core.management.base import BaseCommand

from procrastinate_demos.demo_django import procrastinate_app


class Command(BaseCommand):
    help = "Starts a procrastinate worker"

    def handle(self, *args, **options):
        procrastinate_app.app.run_worker()
