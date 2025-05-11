from datetime import datetime
import boto3
import json
import uuid
import time
from botocore.exceptions import ClientError

# --- Kinesis Consumer ---
def process_kinesis_records():
    REGION = "us-east-1"
    print(":rocket: Iniciando consumidor de Kinesis...")
    kinesis_client = boto3.client('kinesis', region_name=REGION)
    s3_client = boto3.client('s3', region_name=REGION)
    S3_BUCKET = "videoteca-bucket1"
    S3_PREFIX = "videos/"
    stream_name = "video-upload-stream"

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

        for record in records:
            payload = json.loads(record['Data'])
            video_id = payload['video_id']
            print(f":package: Recibido fragmento {payload['chunk_index'] + 1}/{payload['total_chunks']} del video '{payload['filename']}' (ID: {video_id})")

            if payload['chunk_index'] == 0:
                print(f":incoming_envelope: Iniciando la recepción del video: '{payload['filename']}' (ID: {video_id})")

            if video_id not in fragment_buffer:
                fragment_buffer[video_id] = [None] * payload['total_chunks']
            fragment_buffer[video_id][payload['chunk_index']] = bytes.fromhex(payload['data'])

            if all(frag is not None for frag in fragment_buffer[video_id]):
                print(f":jigsaw: Video completo recibido: {payload['filename']} — procesando...")
                file_data_bytes = b''.join(fragment_buffer[video_id])
                filename = payload['filename']
                s3_key = f"{S3_PREFIX}{filename}"

                try:
                    print(f":cloud: Subiendo video '{filename}' a S3...")
                    s3_client.put_object(
                        Bucket=S3_BUCKET,
                        Key=s3_key,
                        Body=file_data_bytes,
                        ContentType="video/mp4"
                    )
                    video_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"
                    print(f":white_check_mark: Video subido a S3: {video_url}")
                except Exception as e:
                    print(f":x: Error al subir a S3: {e}")

                del fragment_buffer[video_id]

        shard_iterator = response['NextShardIterator']
        time.sleep(1)

if __name__ == "__main__":
    process_kinesis_records()
