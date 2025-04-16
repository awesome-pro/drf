import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create the Celery app
app = Celery('core')

# Use string names for configurations so workers don't have to serialize
# Django settings objects
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered Django app configs
app.autodiscover_tasks()

# Define periodic tasks
app.conf.beat_schedule = {
    'check-trial-expirations-daily': {
        'task': 'apps.common.tasks.check_trial_expirations',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight every day
    },
    'send-trial-expiration-reminders': {
        'task': 'apps.common.tasks.send_trial_expiration_reminders',
        'schedule': crontab(hour='*/6'),  # Run every 6 hours
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
