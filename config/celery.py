"""
Celery Configuration for S3 Storage Module
Add this to your main Django project's celery.py
"""

from celery import Celery
from celery.schedules import crontab
import os

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('evol_assistant')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Periodic tasks configuration
app.conf.beat_schedule = {
    'archive-old-documents-daily': {
        'task': 's3_storage.tasks.archive_old_documents',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    'cleanup-temp-files-hourly': {
        'task': 's3_storage.tasks.cleanup_temp_files',
        'schedule': crontab(minute=0),  # Run every hour
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

