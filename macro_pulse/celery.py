import os
from celery import Celery
from celery.schedules import crontab


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macro_pulse.settings')

app = Celery('macro_pulse')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery to use Redis as the result backend and enable task tracking
app.conf.update(
    result_backend='redis://localhost:6379/0',
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,  # Disable prefetching for better task distribution
    task_send_sent_event=True,  # Enable task-sent events
    task_send_started_event=True,  # Enable task-started events
    task_send_received_event=True,  # Enable task-received events
    task_send_success_event=True,  # Enable task-success events
    task_send_retry_event=True,  # Enable task-retry events
    task_send_failure_event=True,  # Enable task-failure events
    worker_send_task_events=True,  # Enable worker task events
    task_store_errors_even_if_ignored=True,  # Store all errors
    broker_connection_retry=True,  # Retry if connection fails
    broker_connection_retry_on_startup=True,  # Retry on startup (new in Celery 6.0)
    broker_connection_max_retries=10,  # Maximum number of retries
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-indicators-every-6-hours': {
        'task': 'indicators.tasks.update_all_indicators',
        'schedule': crontab(hour='*/6'),
    },
} 