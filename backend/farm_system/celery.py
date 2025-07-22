import os
from celery import Celery
from celery.schedules import crontab
import logging

logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_system.settings')

app = Celery('farm_system')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'check-expired-bids': {
        'task': 'bidding.tasks.check_expired_bids',
        'schedule': 30.0,  # Every 30 seconds
    },
    'update-prospect-stats-daily': {
        'task': 'prospects.tasks.update_prospect_stats',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    # 'cleanup-old-bids-daily': {
    #     'task': 'bidding.tasks.cleanup_old_bids',
    #     'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    # },
}

@app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')