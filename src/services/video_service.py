from datetime import datetime
import boto3
import boto3
import os
from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
import uuid
from sqlalchemy import func
from flask import jsonify
from src.api_messages.api_errors import InternalServerError
from src.api_messages.api_videos import VideoDeleted, VideoFailed, VideoListed, VideoUploaded, VideoVoted, VideoRanking, ForbiddenOperation, UsserIssue, VideoIssue
from src.database import db
from src.models.video import Video, VideoSchema
from src.models.vote import Vote, VoteSchema
from src.models.jugador import Jugador, JugadorSchema
from src.tasks.video_tasks import async_save_video

class VideoService:
    
    def save_video(self, jwt_payload, uploadVideo):
        jugador_id = jwt_payload['sub']
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(uploadVideo['video_file'].filename)}"
        file_data = uploadVideo['video_file'].read()

        # --- Kinesis ---
import boto3
import math
import uuid

kinesis_client = boto3.client('kinesis')
KINESIS_STREAM_NAME = os.environ.get('KINESIS_STREAM_NAME', 'video-upload-stream')

video_id = str(uuid.uuid4())
chunk_size = 1024 * 1024  # 1 MB
num_chunks = math.ceil(len(file_data) / chunk_size)

for idx in range(num_chunks):
    chunk_data = file_data[idx * chunk_size:(idx + 1) * chunk_size]
    record = {
        'video_id': video_id,
        'filename': filename,
        'title': uploadVideo['title'],
        'jugador_id': jugador_id,
        'chunk_index': idx,
        'total_chunks': num_chunks,
        'data': chunk_data.hex()  # serializar como string hexadecimal
    }
    # Enviar a Kinesis
    kinesis_client.put_record(
        StreamName=KINESIS_STREAM_NAME,
        Data=json.dumps(record),
        PartitionKey=video_id
    )

        return VideoUploaded("CARGA EN PROCESO. El video se está subiendo en segundo plano.")
    
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