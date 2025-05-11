from datetime import datetime
import os
import boto3
import json
import uuid
from botocore.exceptions import ClientError
from sqlalchemy import inspect
from src.database import db
from src.models.video import Video

# --- Kinesis Consumer ---
def process_kinesis_records():
    kinesis_client = boto3.client('kinesis')
    S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "videoteca-bucket")
    S3_PREFIX = os.environ.get("S3_VIDEO_PREFIX", "videos/")
    stream_name = os.environ.get('KINESIS_STREAM_NAME', 'video-upload-stream')
    shard_iterator = kinesis_client.get_shard_iterator(
        StreamName=stream_name,
        ShardId=kinesis_client.describe_stream(StreamName=stream_name)['StreamDescription']['Shards'][0]['ShardId'],
        ShardIteratorType='TRIM_HORIZON'
    )['ShardIterator']

    fragment_buffer = {}

    while True:
        response = kinesis_client.get_records(ShardIterator=shard_iterator, Limit=100)
        records = response['Records']
        for record in records:
            payload = json.loads(record['Data'])
            video_id = payload['video_id']
            if video_id not in fragment_buffer:
                fragment_buffer[video_id] = [None] * payload['total_chunks']
            fragment_buffer[video_id][payload['chunk_index']] = bytes.fromhex(payload['data'])
            # Si ya tenemos todos los fragmentos
            if all(frag is not None for frag in fragment_buffer[video_id]):
                file_data_bytes = b''.join(fragment_buffer[video_id])
                filename = payload['filename']
                title = payload['title']
                jugador_id = payload['jugador_id']
                s3_key = f"{S3_PREFIX}{filename}" if S3_PREFIX else filename
                s3_client = boto3.client("s3")
                try:
                    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=file_data_bytes, ContentType="video/mp4")
                    video_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"
                    # Registrar en la base de datos
                    from flask import Flask
                    from src.database import get_database_url
                    app = Flask(__name__)
                    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
                    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
                except Exception as e:
                    print(f"Error al subir video a S3 o guardar en DB: {e}")
                # Limpiar buffer
                del fragment_buffer[video_id]
        shard_iterator = response['NextShardIterator']