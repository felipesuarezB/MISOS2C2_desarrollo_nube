import boto3
import json
import threading
import time
from botocore.exceptions import ClientError

REGION = "us-east-1"
S3_BUCKET = "videoteca-bucket1"
S3_PREFIX = "videos/"
STREAM_NAME = "video-upload-stream"

kinesis_client = boto3.client('kinesis', region_name=REGION)
s3_client = boto3.client('s3', region_name=REGION)
fragment_buffer = {}

def process_shard(shard_id):
    print(f"🚀 Iniciando lectura de shard: {shard_id}")
    try:
        shard_iterator = kinesis_client.get_shard_iterator(
            StreamName=STREAM_NAME,
            ShardId=shard_id,
            ShardIteratorType='LATEST'
        )['ShardIterator']
    except ClientError as e:
        print(f"❌ Error al obtener shard iterator: {e}")
        return

    while True:
        response = kinesis_client.get_records(ShardIterator=shard_iterator, Limit=100)
        records = response['Records']

        if not records:
            print(f"⏳ No hay nuevos registros en shard {shard_id}, esperando...")
            time.sleep(1)
            shard_iterator = response['NextShardIterator']
            continue

        for record in records:
            payload = json.loads(record['Data'])
            video_id = payload['video_id']
            chunk_index = payload['chunk_index']
            total_chunks = payload['total_chunks']
            filename = payload['filename']

            print(f"📦 [Shard {shard_id}] Fragmento {chunk_index+1}/{total_chunks} del video '{filename}'")

            if video_id not in fragment_buffer:
                fragment_buffer[video_id] = [None] * total_chunks

            fragment_buffer[video_id][chunk_index] = bytes.fromhex(payload['data'])

            if all(frag is not None for frag in fragment_buffer[video_id]):
                print(f"🧩 Video completo recibido: {filename}, uniendo y subiendo...")

                file_data = b''.join(fragment_buffer[video_id])
                s3_key = f"{S3_PREFIX}{filename}"

                try:
                    s3_client.put_object(
                        Bucket=S3_BUCKET,
                        Key=s3_key,
                        Body=file_data,
                        ContentType="video/mp4"
                    )
                    print(f"✅ Video subido a S3: https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}")
                except Exception as e:
                    print(f"❌ Error al subir a S3: {e}")

                del fragment_buffer[video_id]

        shard_iterator = response['NextShardIterator']
        time.sleep(0.5)

def main():
    print("🔍 Descubriendo shards del stream...")
    try:
        stream_description = kinesis_client.describe_stream(StreamName=STREAM_NAME)
        shards = stream_description['StreamDescription']['Shards']
    except ClientError as e:
        print(f"❌ Error al describir el stream: {e}")
        return

    threads = []
    for shard in shards:
        shard_id = shard['ShardId']
        t = threading.Thread(target=process_shard, args=(shard_id,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
