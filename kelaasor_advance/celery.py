import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kelaasor_advance.settings')

app = Celery('kelaasor_advance')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()