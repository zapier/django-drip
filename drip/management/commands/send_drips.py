from django.core.management.base import BaseCommand

from drip.models import Drip


class Command(BaseCommand):
    def handle(self, *args, **options):
        for drip in Drip.objects.filter(enabled=True):
            drip.drip.run()
