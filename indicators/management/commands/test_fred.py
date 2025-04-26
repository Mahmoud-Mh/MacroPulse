from django.core.management.base import BaseCommand
from indicators.tasks import test_fred_connection

class Command(BaseCommand):
    help = 'Test FRED API connection'

    def handle(self, *args, **options):
        result = test_fred_connection()
        self.stdout.write(self.style.SUCCESS(result)) 