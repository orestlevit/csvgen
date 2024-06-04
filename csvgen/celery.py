import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csvgen")
app = Celery('csvgen')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()