from datetime import datetime
from src.tasks.celery_worker import celery
from src.database import db
from src.models.video import Video
from src.models.jugador import Jugador
from src.models.vote import Vote
import uuid
import os
import boto3
from botocore.exceptions import ClientError
from sqlalchemy import inspect

@celery.task
def async_save_video(jugador_id, title, filename, file_data_bytes):
    print("Guardando archivo en S3")
    try:
        # Configuración de S3
        S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "videoteca-bucket")
        S3_PREFIX = os.environ.get("S3_VIDEO_PREFIX", "videos/")  # puede ser "" si no quieres prefijo
        s3_key = f"{S3_PREFIX}{filename}" if S3_PREFIX else filename

        s3_client = boto3.client("s3")
        # Subir archivo
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=file_data_bytes, ContentType="video/mp4")

        # URL pública
        video_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"

        # Configurar la app de Flask para la DB
        from flask import Flask
        from src.database import get_database_url
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        from src.database import db
        db.init_app(app)

        with app.app_context():
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            if not existing_tables:
                db.create_all()
            video = Video(
                title=title,
                status='subido',
                uploaded_at=datetime.now(),
                processed_at=datetime.now(),
                processed_url=video_url,
                id_jugador=uuid.UUID(jugador_id)
            )
            db.session.add(video)
            db.session.commit()
        return True
    except ClientError as e:
        print(f"Error al subir video a S3: {e}")
        return False
    except Exception as e:
        print(f"Error general al guardar video: {e}")
        return False