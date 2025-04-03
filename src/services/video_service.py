
from datetime import datetime
import os
import uuid
from sqlalchemy import func
from flask import jsonify
from api_messages.api_errors import InternalServerError
from api_messages.api_videos import VideoDeleted, VideoFailed, VideoListed, VideoUploaded, VideoVoted, VideoRanking, ForbiddenOperation, UsserIssue, VideoIssue
from database import db
from models.video import Video, VideoSchema, Vote, VoteSchema
from models.jugador import Jugador, JugadorSchema


class VideoService:
    UPLOAD_FOLDER = 'D:/OneDrive/Videos/' 
    ALLOWED_EXTENSIONS = {'mp4'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in VideoService.ALLOWED_EXTENSIONS

    def save_video(selft, uploadVideo):
        # if file.filename == '' or not VideoService.allowed_file(file.filename):
        #     raise VideoFailed()
        
        # file.seek(0)
        # if len(file.read()) > VideoService.MAX_FILE_SIZE:
        #     raise VideoFailed()
        # file.seek(0)
        
        #filename = secure_filename(file.filename)
        # file_path = os.path.join(VideoService.UPLOAD_FOLDER, filename)
        # file.save(file_path)
        
        video = Video(
            title=uploadVideo['title'], 
            status='subido', 
            uploaded_at=datetime.now(), 
            processed_at=datetime.now(), 
            processed_url="https://example.com/processed_video.mp4",
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
    
    def list_ranking_videos(self, jwt_payload):
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