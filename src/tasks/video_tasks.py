from datetime import datetime
from src.tasks.celery_worker import celery
from src.database import db
from src.models.video import Video
# Import all models to ensure tables are created
from src.models.jugador import Jugador
from src.models.vote import Vote
import boto3
import uuid
import os

S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")

@celery.task
def async_save_video(jugador_id, title, filename, file_data_bytes):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name=S3_REGION
    )

    from io import BytesIO
    file_data = BytesIO(file_data_bytes)

    s3.upload_fileobj(file_data, S3_BUCKET, filename, ExtraArgs={"ContentType": "video/mp4"})

    video_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"
    
    try:
        # Use the Flask app to get properly configured database session
        from flask import Flask
        from src.database import get_database_url
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize the database with the app
        from src.database import db
        db.init_app(app)
        
        # Create app context and save the video
        with app.app_context():
            # Make sure all tables exist
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
        print(f"Error saving video to database: {e}")
        return False