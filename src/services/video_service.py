
from datetime import datetime
import boto3
import os
from werkzeug.utils import secure_filename
import uuid

from flask import jsonify
from api_messages.api_errors import InternalServerError
from api_messages.api_videos import VideoDeleted, VideoFailed, VideoListed, VideoUploaded, VideoVoted, VideoRanking
from database import db
from models.video import Video, VideoSchema

# Configuración de S3
S3_BUCKET = "tu-bucket"
S3_REGION = "us-east-2"
S3_ACCESS_KEY = ""
S3_SECRET_KEY = ""

s3_client = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)


class VideoService:
    
    def save_video(selft, uploadVideo):        
        if not uploadVideo['video_file'] or uploadVideo['video_file'].filename.split('.')[-1].lower() != "mp4":
            return {"error": "Solo se permiten archivos MP4"}, 400

        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(uploadVideo['video_file'].filename)}"
        s3_client.upload_fileobj(uploadVideo['video_file'], S3_BUCKET, filename, ExtraArgs={"ContentType": "video/mp4"})

        video_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"
        
        video = Video(
            title=uploadVideo['title'], 
            status='subido', 
            uploaded_at=datetime.now(), 
            processed_at=datetime.now(), 
            processed_url=video_url,
            id_jugador=uuid.UUID(uploadVideo["id_jugador"]))
        
        db.session.add(video)
        db.session.commit()
        
        # try:
        #     db.session.add(video)
        #     db.session.commit()
        # except Exception as ex:
        #     db.session.rollback()
        #     raise InternalServerError() from ex
                
        return VideoUploaded(video.id)
    
    def list_videos(self, jwt_payload):
        jugador_id = jwt_payload['sub']
        id_jugador_uuid = uuid.UUID(jugador_id)

        found_videos = []
        try:
            found_videos = db.session.query(Video).filter(Video.id_jugador == id_jugador_uuid).all()
        except Exception as ex:
            raise InternalServerError() from ex
        
        found_videos_json = [VideoSchema().dump(video) for video in found_videos]

        return VideoListed(found_videos_json)
    
    def list_public_videos(self, jwt_payload):
        
        found_videos = []
        try:
            found_videos = db.session.query(Video).all()
        except Exception as ex:
            raise InternalServerError() from ex
        
        found_videos_json = [VideoSchema().dump(video) for video in found_videos]

        return VideoListed(found_videos_json)

    def get_video(self, id_video):
        id_video_uuid = uuid.UUID(id_video)
        found_video = None
        try:
            found_video = db.session.query(Video).filter(Video.id == id_video_uuid).first()
        except Exception as ex:
            raise InternalServerError() from ex

        if not found_video:
            return VideoFailed()
        
        found_video_json = VideoSchema().dump(found_video) 

        return VideoListed(found_video_json)
    
    def delete_video(self, id_video):
        id_video_uuid = uuid.UUID(id_video)
        found_video = None
        try:
            found_video = db.session.query(Video).filter(Video.id == id_video_uuid).first()
        except Exception as ex:
            raise InternalServerError() from ex

        if not found_video:
            return VideoFailed()

        db.session.delete(found_video)
        db.session.commit()

        return VideoDeleted(id_video)
    
    def vote_video(self, id_video):
        id_video_uuid = uuid.UUID(id_video)
        found_video = None
        try:
            found_video = db.session.query(Video).filter(Video.id == id_video_uuid).first()
            found_video.vote += 1
        except Exception as ex:
            raise InternalServerError() from ex

        if not found_video:
            return VideoFailed()
        
        db.session.commit()
        return VideoVoted()
    
    def list_ranking_videos(self, jwt_payload):
        found_videos = []
        try:
            found_videos = db.session.query(Video).order_by(Video.vote.desc()).all()

        except Exception as ex:
            raise InternalServerError() from ex
        
        found_videos_json = [VideoSchema().dump(video) for video in found_videos]

        return VideoRanking(found_videos_json)

    
video_service = VideoService()