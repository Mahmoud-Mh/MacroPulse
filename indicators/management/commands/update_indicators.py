from django.core.management.base import BaseCommand
from indicators.tasks import update_indicator

class Command(BaseCommand):
    help = 'Update all indicators from FRED'

    def handle(self, *args, **options):
        # List of important economic indicators from FRED
        INDICATORS = {
            'GDP': 'GDP',
            'Unemployment Rate': 'UNRATE',
            'CPI': 'CPIAUCSL',
            'Federal Funds Rate': 'FEDFUNDS',
            'Industrial Production': 'INDPRO',
            'Consumer Sentiment': 'UMCSENT',
            'Retail Sales': 'RSXFS',
            'Housing Starts': 'HOUST',
            'PCE': 'PCE',
            'M2': 'M2'
        }
        
        for name, series_id in INDICATORS.items():
            self.stdout.write(f"Updating {name}...")
            try:
                update_indicator(series_id=series_id)
                self.stdout.write(self.style.SUCCESS(f"Successfully updated {name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to update {name}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS('Finished updating all indicators')) 