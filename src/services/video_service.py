
from datetime import datetime
import boto3
import os
from werkzeug.utils import secure_filename
import uuid
from sqlalchemy import func
from flask import jsonify
from api_messages.api_errors import InternalServerError
from api_messages.api_videos import VideoDeleted, VideoFailed, VideoListed, VideoUploaded, VideoVoted, VideoRanking, ForbiddenOperation, UsserIssue, VideoIssue
from database import db
from models.video import Video, VideoSchema
from models.vote import Vote, VoteSchema
from models.jugador import Jugador, JugadorSchema

# Configuración de S3
S3_BUCKET = "my-bucket-for-cloud-api"
S3_REGION = "us-east-2"
#S3_ACCESS_KEY = ""
#S3_SECRET_KEY = ""

s3_client = boto3.client(
    "s3",
    #aws_access_key_id=S3_ACCESS_KEY,
    #aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)


class VideoService:
    
    def save_video(self,jwt_payload, uploadVideo): 
        jugador_id = jwt_payload['sub']
        id_jugador_uuid = uuid.UUID(jugador_id)
        print(str(uploadVideo)+"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if not uploadVideo['video_file'] or uploadVideo['video_file'].filename.split('.')[-1].lower() != "mp4":
            return {"error": "Solo se permiten archivos MP4"}, 400

        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(uploadVideo['video_file'].filename)}"
        s3_client.upload_fileobj(uploadVideo['video_file'], S3_BUCKET, filename, ExtraArgs={"ContentType": "video/mp4"})


        # Guardar metadata en la BD
        video_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"
        video = Video(
            title=uploadVideo['title'],
            status='subido',
            uploaded_at=datetime.now(),
            processed_at=datetime.now(),
            processed_url=video_url,
            id_jugador=id_jugador_uuid)
        
        db.session.add(video)
        db.session.commit()
        return VideoUploaded(video.id)
        
        # try:
        #     db.session.add(video)
        #     db.session.commit()
        # except Exception as ex:
        #     db.session.rollback()
        #     raise InternalServerError() from ex
                
    
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
    
    def vote_video(self, id_video, username):
        id_video_uuid = uuid.UUID(id_video)
        id_jugador_uuid = uuid.UUID(username)
        print(f"✅ ID de jugador convertido: {id_jugador_uuid} (tipo: {type(id_jugador_uuid)})")
        found_video = None
        found_jugador = None

        try:
            # 1️⃣ Buscar el video
            found_video = db.session.query(Video).filter(Video.id == id_video_uuid).first()
            if not found_video:
                return VideoIssue()

            # 2️⃣ Buscar el usuario
            found_jugador = db.session.query(Jugador).filter(Jugador.id == id_jugador_uuid).first()
            if not found_jugador:
                return UsserIssue()

            # 3️⃣ Verificar si el usuario ya votó por este video
            voto_existente = db.session.query(Vote).filter_by(video_id=id_video_uuid, jugador_id=found_jugador.id).first()
            
            if voto_existente:
                return ForbiddenOperation()

            # 4️⃣ Registrar el voto
            nuevo_voto = Vote(video_id=id_video_uuid, jugador_id=found_jugador.id, value=1)  # Se asume que el voto es positivo (1)
            db.session.add(nuevo_voto)
            db.session.commit()

            return VideoVoted()

        except Exception as ex:
            db.session.rollback()
            raise InternalServerError() from ex
    
    def list_ranking_videos(self):
        found_videos = []
        try:
            found_videos = (
                db.session.query(Video.id, Video.title, func.count(Vote.id).label("vote_count"))
                .join(Vote, Video.id == Vote.video_id)
                .group_by(Video.id, Video.title)
                .order_by(func.count(Vote.id).desc())
                .all()
            )

        except Exception as ex:
            raise InternalServerError() from ex
        
        found_videos_json = [{"id": str(video_id), "title": title, "vote_count": vote_count}  for video_id, title, vote_count in found_videos]

        return VideoRanking(found_videos_json)

    
video_service = VideoService()