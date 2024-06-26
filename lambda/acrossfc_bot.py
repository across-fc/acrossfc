import json

# Local
from acrossfc.ext import discord_client as DISCORD_API

DISCORD_CHANNEL_ID = '1242662415670317128'


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
        # Application commands
        command_name = body['data']['name']
        if command_name == "fc_points":
            interaction_id = body['id']
            interaction_token = body['token']
            DISCORD_API.post(f"interactions/{interaction_id}/{interaction_token}/callback", {
                'type': 4,
                'data': {
                    'content': 'Points for the current tier are now closed. The next tier will begin on <t:1719565200:f>.',
                    'flags': 1 << 6
                }
            })
        # TODO: Implement button callbacks too
    return {
        'statusCode': 200,
        'body': json.dumps({'type': 1})
    }
