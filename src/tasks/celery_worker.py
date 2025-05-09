from celery import Celery
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar Celery con Amazon SQS
celery = Celery(
    'src',
    broker='sqs://',
    include=['src.tasks.video_tasks']
)

# Configurar opciones de transporte SQS
celery.conf.broker_transport_options = {
    'region': os.getenv('AWS_REGION', 'us-east-1'),
    'visibility_timeout': 3600,  # tiempo máximo que un worker tiene un mensaje
    'polling_interval': 1,  # segundos entre chequeos de nueva tarea
}

celery.conf.task_default_queue = 'sqs-task-videos'
celery.conf.timezone = 'UTC'
