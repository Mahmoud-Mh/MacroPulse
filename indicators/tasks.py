import logging
from celery import shared_task
from django.conf import settings
from fredapi import Fred
from .models import Indicator, Task
from django.utils import timezone

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

@shared_task(bind=True, name='indicators.run_task')
def run_task(self, task_id):
    """
    Run a task by its ID.
    """
    try:
        # Update task state to STARTED
        self.update_state(state='STARTED', meta={'task_id': task_id})
        
        task = Task.objects.get(id=task_id)
        # Update last run time
        task.last_run = timezone.now()
        task.save(update_fields=['last_run'])
        
        # Simulate some work
        self.update_state(state='PROGRESS', meta={'task_id': task_id, 'status': 'Processing'})
        
        # Here you can add the actual task logic
        result = f"Task {task.name} started"
        
        return {
            'status': 'SUCCESS',
            'task_id': task_id,
            'message': result,
            'last_run': task.last_run.isoformat()
        }
        
    except Task.DoesNotExist:
        self.update_state(state='FAILURE', meta={
            'exc_type': 'Task.DoesNotExist',
            'exc_message': f"Task with ID {task_id} not found"
        })
        raise
    except Exception as e:
        self.update_state(state='FAILURE', meta={
            'exc_type': type(e).__name__,
            'exc_message': str(e)
        })
        raise

@shared_task
def health_check_task():
    return "ok"

@shared_task(bind=True, name='indicators.run_manual_task')
def run_manual_task(self, task_id):
    """
    Run a manual task by its ID.
    """
    logger.info(f"Starting manual task execution for task_id: {task_id}")
    try:
        # Update task state to STARTED
        self.update_state(state='STARTED', meta={'task_id': task_id})
        logger.debug(f"Task {task_id} state set to STARTED")
        
        task = Task.objects.get(id=task_id)
        logger.info(f"Found task: {task.name} (ID: {task_id})")
        
        # Update last run time with timezone-aware datetime
        task.last_run = timezone.now()
        task.save(update_fields=['last_run'])
        logger.debug(f"Updated last_run time for task {task_id}")
        
        # Simulate some work
        self.update_state(state='PROGRESS', meta={
            'task_id': task_id, 
            'status': 'Processing',
            'last_run': task.last_run.isoformat()
        })
        logger.debug(f"Task {task_id} state set to PROGRESS")
        
        # Here you can add the actual task logic
        result = f"Task {task.name} completed successfully"
        logger.info(result)
        
        # Refresh task to ensure we have the latest data
        task.refresh_from_db()
        logger.debug(f"Task {task_id} refreshed from database")
        
        return {
            'status': 'SUCCESS',
            'task_id': task_id,
            'message': result,
            'last_run': task.last_run.isoformat()
        }
    except Task.DoesNotExist:
        error_msg = f"Task with ID {task_id} not found"
        logger.error(error_msg)
        self.update_state(state='FAILURE', meta={
            'exc_type': 'Task.DoesNotExist',
            'exc_message': error_msg
        })
        raise
    except Exception as e:
        error_msg = f"Error executing task {task_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)  # Include full traceback
        self.update_state(state='FAILURE', meta={
            'exc_type': type(e).__name__,
            'exc_message': str(e)
        })
        raise

@shared_task(bind=True, name='indicators.run_scheduled_task')
def run_scheduled_task(self, task_id):
    """
    Run a scheduled task by its ID.
    """
    logger.info(f"Starting scheduled task execution for task_id: {task_id}")
    try:
        # Update task state to STARTED
        self.update_state(state='STARTED', meta={'task_id': task_id})
        logger.debug(f"Task {task_id} state set to STARTED")
        
        task = Task.objects.get(id=task_id)
        logger.info(f"Found task: {task.name} (ID: {task_id}, Status: {task.status})")
        
        if task.status == 'Active':
            # Update last run time with timezone-aware datetime
            task.last_run = timezone.now()
            task.save(update_fields=['last_run'])
            logger.debug(f"Updated last_run time for task {task_id}")
            
            # Simulate some work
            self.update_state(state='PROGRESS', meta={
                'task_id': task_id, 
                'status': 'Processing',
                'last_run': task.last_run.isoformat()
            })
            logger.debug(f"Task {task_id} state set to PROGRESS")
            
            # Here you can add the actual task logic
            result = f"Scheduled task {task.name} completed successfully"
            logger.info(result)
            
            # Refresh task to ensure we have the latest data
            task.refresh_from_db()
            logger.debug(f"Task {task_id} refreshed from database")
            
            return {
                'status': 'SUCCESS',
                'task_id': task_id,
                'message': result,
                'last_run': task.last_run.isoformat()
            }
        
        logger.info(f"Task {task_id} ({task.name}) is inactive, skipping execution")
        self.update_state(state='IGNORED', meta={
            'task_id': task_id,
            'message': f"Task {task.name} is inactive"
        })
        return {
            'status': 'IGNORED',
            'task_id': task_id,
            'message': f"Task {task.name} is inactive"
        }
    except Task.DoesNotExist:
        error_msg = f"Task with ID {task_id} not found"
        logger.error(error_msg)
        self.update_state(state='FAILURE', meta={
            'exc_type': 'Task.DoesNotExist',
            'exc_message': error_msg
        })
        raise
    except Exception as e:
        error_msg = f"Error executing task {task_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)  # Include full traceback
        self.update_state(state='FAILURE', meta={
            'exc_type': type(e).__name__,
            'exc_message': str(e)
        })
        raise 