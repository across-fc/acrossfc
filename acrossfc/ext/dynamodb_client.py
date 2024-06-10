import json
import logging
from typing import Dict

# 3rd-party
import boto3

LOG = logging.getLogger(__name__)


def upload_clear_rates(data: Dict):
    # TODO: Make this configurable
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
        LOG.info("Clear rates updated in DB successfully:", response)
    except Exception as e:
        LOG.error("Error upserting item:", e)
