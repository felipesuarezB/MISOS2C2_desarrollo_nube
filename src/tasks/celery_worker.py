from celery import Celery

celery = Celery(
    'video_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery.conf.timezone = 'UTC'