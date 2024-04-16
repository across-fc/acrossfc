import sys
import json
import boto3
import redis
from datetime import date
from ffxiv_clear_rates.main import run


def lambda_handler(event, context):
    LOCAL_DB_FILENAME = '/tmp/database'
    sys.argv = [
        'main.py',
        'clear_rates',
        '-w', LOCAL_DB_FILENAME,
        '-pd',
        '--prod'
    ]
    data = run()

    print('Finished processing FFLogs data.')

    # Upload database to S3
    s3 = boto3.client('s3')
    bucket_name = 'ffxiv-clear-rates'
    object_key = f'database/{date.today()}'
    try:
        s3.upload_file(LOCAL_DB_FILENAME, bucket_name, object_key)
        print(f"{object_key} uploaded successfully")
    except Exception as e:
        print(f"Error uploading {object_key}: {e}")

    # Update cache
    redis_client = redis.Redis(
        host='ffxiv-clear-rates-7rpxnm.serverless.usw2.cache.amazonaws.com',
        port=6379,
        db=0,
        password=None,
        ssl=True
    )
    redis_client.set('latest', json.dumps(data))
    print("Clear rates stored in Redis successfully.")

    return {
        'statusCode': 200,
        'body': 'Success'
    }
