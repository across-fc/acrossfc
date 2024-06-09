import sys
import json
import boto3
from datetime import date
from acrossfc.api.main import run


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

    # Update DB
    TABLE_NAME = 'ffxiv_clear_rates'
    item = {
        'record_date': {'S': 'latest'},
        'value': {
            'S': json.dumps(data)
        },
    }
    dynamodb = boto3.client('dynamodb')
    try:
        # Try to update the item
        response = dynamodb.put_item(
            TableName=TABLE_NAME,
            Item=item,
            ConditionExpression='attribute_not_exists(record_date)'
        )
        print("Item upserted successfully: ", response)
    except dynamodb.exceptions.ConditionalCheckFailedException:
        # If the item already exists, perform an update
        response = dynamodb.update_item(
            TableName=TABLE_NAME,
            Key={'record_date': {'S': 'latest'}},
            UpdateExpression='SET #attribute_name = :val1',
            # Define the attributes and values to update
            ExpressionAttributeNames={
                '#attribute_name': 'value',
            },
            ExpressionAttributeValues={
                ':val1': item['value'],
            }
        )
        print("Clear rates updated in DB successfully:", response)
    except Exception as e:
        print("Error upserting item:", e)

    return data
