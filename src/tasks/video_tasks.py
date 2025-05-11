from datetime import datetime
import os
import boto3
import json
import uuid
import time
from botocore.exceptions import ClientError
from sqlalchemy import inspect
from src.database import db
from src.models.video import Video

# --- Kinesis Consumer ---
def process_kinesis_records():
    REGION = "us-east-1"
    print(":rocket: Iniciando consumidor de Kinesis...")
    kinesis_client = boto3.client('kinesis', region_name=REGION)
    s3_client = boto3.client('s3', region_name=REGION)
    S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "videoteca-bucket1")
    S3_PREFIX = os.environ.get("S3_VIDEO_PREFIX", "videos/")
    stream_name = os.environ.get('KINESIS_STREAM_NAME', 'video-upload-stream')

    # Obtener shard iterator
    try:
        stream_description = kinesis_client.describe_stream(StreamName=stream_name)
        shard_id = stream_description['StreamDescription']['Shards'][0]['ShardId']
        shard_iterator = kinesis_client.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard_id,
            ShardIteratorType='TRIM_HORIZON'
        )['ShardIterator']
        print(f":white_check_mark: Obtenido shard iterator del stream '{stream_name}' (shard ID: {shard_id})")
    except ClientError as e:
        print(f":x: Error al obtener el shard iterator: {e}")
        return

    fragment_buffer = {}
    while True:
        response = kinesis_client.get_records(ShardIterator=shard_iterator, Limit=100)
        records = response['Records']

        if not records:
            print(":hourglass_flowing_sand: Esperando nuevos registros en el stream...")

        for record in records:
            payload = json.loads(record['Data'])
            video_id = payload['video_id']
            print(f":package: Recibido fragmento {payload['chunk_index'] + 1}/{payload['total_chunks']} del video '{payload['filename']}' (ID: {video_id})")
            
            # Log al recibir un archivo
            if payload['chunk_index'] == 0:
                print(f":incoming_envelope: Iniciando la recepción del video: '{payload['filename']}' (ID: {video_id})")

            if video_id not in fragment_buffer:
                fragment_buffer[video_id] = [None] * payload['total_chunks']
            fragment_buffer[video_id][payload['chunk_index']] = bytes.fromhex(payload['data'])

            # Si ya tenemos todos los fragmentos
            if all(frag is not None for frag in fragment_buffer[video_id]):
                print(f":jigsaw: Video completo recibido: {payload['filename']} — procesando...")
                file_data_bytes = b''.join(fragment_buffer[video_id])
                filename = payload['filename']
                title = payload['title']
                jugador_id = payload['jugador_id']
                s3_key = f"{S3_PREFIX}{filename}" if S3_PREFIX else filename

                try:
                    # Subir a S3
                    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=file_data_bytes, ContentType="video/mp4")
                    video_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"
                    print(f":white_check_mark: Video subido a S3: {video_url}")
                    
                    # Registrar en DB
                    from flask import Flask
                    from src.database import get_database_url
                    app = Flask(__name__)
                    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
                    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
                    db.init_app(app)
                    
                    with app.app_context():
                        inspector = inspect(db.engine)
                        if not inspector.has_table("videos"):
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
                        print(f":inbox_tray: Registro guardado en DB para video: {title} (Jugador ID: {jugador_id})")
                except Exception as e:
                    print(f":x: Error al subir a S3 o registrar en DB: {e}")

                # Limpiar buffer
                del fragment_buffer[video_id]

        # Actualizar el shard iterator y esperar antes de la siguiente lectura
        shard_iterator = response['NextShardIterator']
        time.sleep(1)  # :white_check_mark: Importante para evitar throttling y permitir llegada de datos nuevos

if __name__ == "__main__":
    process_kinesis_records()
