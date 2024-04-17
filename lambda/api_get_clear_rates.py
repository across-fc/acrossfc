import json
import boto3

def lambda_handler(event, context):
    # Initialize a DynamoDB client
    dynamodb = boto3.client('dynamodb')
    
    try:
        # Retrieve item from DynamoDB table
        response = dynamodb.get_item(
            TableName='ffxiv_clear_rates',
            Key={
                'record_date': {
                    'S': 'latest'
                }
            }
        )
        item = response.get('Item')
        if item:
            return json.loads(item['value']['S'])
        else:
            print("Record not found.")

    except Exception as e:
        print("Error getting record:", e)
