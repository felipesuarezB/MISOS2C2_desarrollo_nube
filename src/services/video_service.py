from datetime import datetime
import boto3
import os
from werkzeug.utils import secure_filename
import uuid
import math
import json
from sqlalchemy import func
from flask import jsonify
from src.api_messages.api_errors import InternalServerError
from src.api_messages.api_videos import VideoDeleted, VideoFailed, VideoListed, VideoUploaded, VideoVoted, VideoRanking, ForbiddenOperation, UsserIssue, VideoIssue
from src.database import db
from src.models.video import Video, VideoSchema
from src.models.vote import Vote, VoteSchema
from src.models.jugador import Jugador, JugadorSchema

class VideoService:
    
    def save_video(self, jwt_payload, uploadVideo):
        jugador_id = jwt_payload['sub']
        original_filename = uploadVideo['video_file'].filename
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(original_filename)}"
        file_data = uploadVideo['video_file'].read()
        
        # Log del tamaño del archivo recibido
        file_size_kb = len(file_data) / 1024
        print(f"📥 Archivo recibido: {original_filename}")
        print(f"🗂️ Nombre seguro: {filename}")
        print(f"📏 Tamaño del archivo: {file_size_kb:.2f} KB")
        
        kinesis_client = boto3.client(
            'kinesis',
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )

        KINESIS_STREAM_NAME = os.environ.get('KINESIS_STREAM_NAME', 'video-upload-stream')
        video_id = str(uuid.uuid4())

        # Máximo de bytes crudos por chunk:
        MAX_KINESIS_PAYLOAD = 1048576  # 1 MB
        json_overhead_estimate = 1024  # estimación conservadora de 1 KB para campos, comillas, etc.

        # Calculamos el tamaño del chunk
        chunk_size = (MAX_KINESIS_PAYLOAD - json_overhead_estimate) // 2  # dado que .hex() duplica el tamaño
        num_chunks = math.ceil(len(file_data) / chunk_size)

        # Log del número de chunks
        print(f"📦 Dividiendo archivo en {num_chunks} fragmentos de hasta {chunk_size} bytes cada uno")

        # Enviar fragmentos a Kinesis
        for idx in range(num_chunks):
            chunk_data = file_data[idx * chunk_size:(idx + 1) * chunk_size]
            chunk_size_actual = len(chunk_data)  # Tamaño real del chunk

            record = {
                'video_id': video_id,
                'filename': filename,
                'title': uploadVideo['title'],
                'jugador_id': jugador_id,
                'chunk_index': idx,
                'total_chunks': num_chunks,
                'data': chunk_data.hex()  # serializar como string hexadecimal
            }

            try:
                kinesis_client.put_record(
                    StreamName=KINESIS_STREAM_NAME,
                    Data=json.dumps(record),
                    PartitionKey=video_id
                )
                # Log del envío de cada chunk
                print(f"✅ Chunk {idx+1}/{num_chunks} enviado a Kinesis, tamaño: {chunk_size_actual} bytes")
            except Exception as e:
                # Log de error al enviar chunk
                print(f"❌ Error al enviar chunk {idx+1}: {e}")
                raise InternalServerError() from e

        # Log final de carga exitosa
        print(f"🎉 Video '{filename}' enviado completo con ID: {video_id}")
        return VideoUploaded(video_id)
    
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

# Instanciando el servicio
video_service = VideoService()
