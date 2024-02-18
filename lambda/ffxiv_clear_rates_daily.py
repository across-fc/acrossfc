import sys
import boto3
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
    run()

    # Upload database to S3
    s3 = boto3.client('s3')
    bucket_name = 'ffxiv-clear-rates'
    object_key = f'database/{date.today()}'
    try:
        s3.upload_file(LOCAL_DB_FILENAME, bucket_name, object_key)
        print(f"{object_key} uploaded successfully")
    except Exception as e:
        print(f"Error uploading {object_key}: {e}")

    return {
        'statusCode': 200,
        'body': 'Success'
    }
