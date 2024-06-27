import json

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.ext import discord_client as DISCORD_API
from acrossfc.ext.discord_client import Interaction
from acrossfc.ext.ddb_client import DDB_CLIENT
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT

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

    if body['type'] == 2:
        # Application commands
        command_name = body['data']['name']
        if command_name == "fc_points":
            interaction_id = body['id']
            interaction_token = body['token']
            discord_user_id = body['member']['user']['id']
            interaction = Interaction(interaction_id, interaction_token)

            member_id = DDB_CLIENT.get_member_id(int(discord_user_id))
            if member_id is None:
                interaction.respond('Oops, we are unable to find you in our database. If you are an FC member, please reach out to an admin.')
            else:
                interaction.thinking('...holup...')
                is_fc = FFLOGS_CLIENT.is_member_in_guild(member_id)
                if not is_fc:
                    interaction.followup('This function is only available to FC members. If you are new, please reach out to <@!795916443891531786>')
                else:
                    total_points = DDB_CLIENT.get_member_total_points(member_id, FC_CONFIG.current_submissions_tier)
                    if total_points is None:
                        total_points = 0
                    interaction.followup(f'You currently have {total_points} points.')
        # TODO: Implement button callbacks too
    return {
        'statusCode': 200,
        'body': json.dumps({'type': 1})
    }
