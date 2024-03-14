import asyncio
import os

from celery import Celery

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get('CELERY_BROKER_URL')
celery.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND')
broker_connection_retry_on_startup = True

celery.autodiscover_tasks(['app.tasks.tasks'])

loop = asyncio.new_event_loop()
