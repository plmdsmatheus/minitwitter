import os
from celery import Celery

# Default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('backend')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Dicover tasks from all registered Django app configs.
app.autodiscover_tasks()