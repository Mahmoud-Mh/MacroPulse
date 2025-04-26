import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macro_pulse.settings')

app = Celery('macro_pulse')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-indicators-every-6-hours': {
        'task': 'indicators.tasks.update_all_indicators',
        'schedule': crontab(hour='*/6'),
    },
} 