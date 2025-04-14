from datetime import datetime
from src.tasks.celery_worker import celery
from src.database import db
from src.models.video import Video
from src.models.jugador import Jugador
from src.models.vote import Vote
import uuid
import os
from sqlalchemy import inspect

# Ruta local en el EC2
LOCAL_VIDEO_PATH = os.path.expanduser("~/shared_folder")
IP_PUBBLICA_NFS = "44.203.22.5"

@celery.task
def async_save_video(jugador_id, title, filename, file_data_bytes):
    
    print(f"Guardando archivo en: {LOCAL_VIDEO_PATH}")
    try:
        # Crear el directorio si no existe
        os.makedirs(LOCAL_VIDEO_PATH, exist_ok=True)
        
        # Ruta completa del archivo
        file_path = os.path.join(LOCAL_VIDEO_PATH, filename)
        
        # Escribir el archivo en disco
        with open(file_path, "wb") as f:
            f.write(file_data_bytes)

        # URL o ruta pública que se usará (puedes ajustarla según cómo sirvas los archivos)
        video_url = f"http://{IP_PUBBLICA_NFS}/videos/{filename}"

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

    except Exception as e:
        print(f"Error saving video to local disk or database: {e}")
        return False