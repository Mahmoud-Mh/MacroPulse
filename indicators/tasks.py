import logging
from celery import shared_task
from django.conf import settings
from fredapi import Fred
from .models import Indicator

logger = logging.getLogger(__name__)
fred = Fred(api_key=settings.FRED_API_KEY)

def test_fred_connection():
    """
    Test function to verify FRED API connection and data fetching.
    """
    try:
        # Try fetching GDP data
        series_id = 'GDP'
        series_info = fred.get_series_info(series_id)
        series_data = fred.get_series(series_id)
        
        if series_data.empty:
            return "No data found for GDP"
        
        # Get the latest data point
        latest_value = series_data.iloc[-1]
        latest_date = series_data.index[-1]
        
        return f"Successfully fetched GDP data: {latest_value} as of {latest_date}"
        
    except Exception as exc:
        return f"Error: {str(exc)}"

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 min
)
def update_indicator(self, series_id, country="US"):
    """
    Update a single indicator from FRED API.
    """
    try:
        print(f"Fetching data for {series_id}")
        # Get series information
        series_info = fred.get_series_info(series_id)
        series_data = fred.get_series(series_id)
        
        if series_data.empty:
            print(f"No data found for series {series_id}")
            return
        
        # Get the latest data point
        latest_value = series_data.iloc[-1]
        latest_date = series_data.index[-1]
        
        print(f"Got data for {series_id}: {latest_value} as of {latest_date}")
        
        indicator, created = Indicator.objects.update_or_create(
            name=series_info.title,
            country=country,
            defaults={
                'value': float(latest_value),
                'unit': series_info.units,
                'category': series_info.frequency,
                'frequency': series_info.frequency,
                'description': series_info.notes,
                'last_update': latest_date,
                'source': 'FRED'
            }
        )
        
        print(f"{'Created' if created else 'Updated'} indicator: {indicator}")
        return True
        
    except Exception as exc:
        print(f"Error updating series {series_id}: {exc}")
        raise exc

@shared_task
def update_all_indicators():
    """
    Update all common FRED indicators.
    """
    # List of economic indicators from FRED
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
        try:
            update_indicator(series_id=series_id)
        except Exception as e:
            logger.error(f"Error updating {name}: {e}")
    
    logger.info(f"Updated {len(INDICATORS)} indicators")
    return True

@shared_task
def health_check_task():
    return "ok" 