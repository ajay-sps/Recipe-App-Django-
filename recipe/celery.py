from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE','recipe.settings')
app = Celery('recipe')
app.conf.enable_utc = False
app.conf.update(timezone = 'Asia/Kolkata')
# Configure Celery using Django's settings
# app.config_from_object('django.conf:settings')
app.config_from_object(settings,namespace='CELERY')
# Load task modules from all registered Django app configs
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS\)
app.autodiscover_tasks()