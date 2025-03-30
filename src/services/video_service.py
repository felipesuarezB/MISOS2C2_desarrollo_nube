
from datetime import datetime
import os
import uuid

from flask import jsonify
from api_messages.api_errors import InternalServerError
from api_messages.api_videos import VideoDeleted, VideoFailed, VideoListed, VideoUploaded, VideoVoted, VideoRanking
from database import db
from models.video import Video, VideoSchema


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