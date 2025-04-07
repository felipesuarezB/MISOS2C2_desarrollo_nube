from celery import Celery
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar Celery con valores de entorno o predeterminados
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery(
    'src',
    broker=broker_url,
    backend=result_backend,
    include=['src.tasks.video_tasks']
)

celery.conf.timezone = 'UTC'