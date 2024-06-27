import json
import requests

# Local
from acrossfc.core.config import FC_CONFIG


def validate_request(event):
    from nacl.signing import VerifyKey
    from nacl.exceptions import BadSignatureError

    # Your public key can be found on your application in the Developer Portal
    PUBLIC_KEY = '739c36d51d0c0828dc8d67099abd48675d39f8928eb8e0941c5d3d326d9d4b3b'

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    signature = event['headers']["x-signature-ed25519"]
    timestamp = event['headers']["x-signature-timestamp"]
    body = event['body']

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        return True
    except BadSignatureError:
        return False


def lambda_handler(event, context):
    if not validate_request(event):
        return {
            'statusCode': 401
        }

    # Add CORS headers to the response
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

    http_method = event['requestContext']['http']['method']
    if http_method == 'OPTIONS':
        # Handle preflight request
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps('CORS preflight response')
        }

    # Read the event to determine the type of request
    body = json.loads(event.get('body', '{}'))

    if body['type'] == 1:
        # Respond to Discord's PING event
        return {
            'statusCode': 200,
            'body': json.dumps({'type': 1})
        }
    elif body['type'] == 2:
        interaction_id = body['id']
        interaction_token = body['token']
        url = f'https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback'
        headers = {
            'Authorization': f'Bot {FC_CONFIG.discord_bot_token}',
            'Content-Type': 'application/json'
        }
        json_data = {
            'type': 4,
            'data': {
                'content': f"We have {len(roster)} members!"
            }
        }
        response = requests.post(url, headers=headers, json=json_data)
        return response.json()

    return {
        'statusCode': 200,
        'body': json.dumps({'type': 1})
    }
