import json

# Local
from acrossfc import ANALYTICS_LOG
from acrossfc.core.config import FC_CONFIG
from acrossfc.ext.discord_client import Interaction
from acrossfc.ext.ddb_client import DDB_CLIENT
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT


def validate_request(event):
    from nacl.signing import VerifyKey
    from nacl.exceptions import BadSignatureError

    verify_key = VerifyKey(bytes.fromhex(FC_CONFIG.discord_app_public_key))

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
        discord_user_id = body['member']['user']['id']
        ANALYTICS_LOG.info(f"{discord_user_id} {command_name}")

        if command_name == "fc_points":
            interaction_id = body['id']
            interaction_token = body['token']
            interaction = Interaction(interaction_id, interaction_token)
            interaction.thinking()

            member_id = DDB_CLIENT.get_member_id(int(discord_user_id))
            if member_id is None:
                interaction.update_msg('Oops, we are unable to find you in our database. If you are an FC member, please reach out to an admin.')
            else:
                is_fc = FFLOGS_CLIENT.is_member_in_guild(member_id)
                if not is_fc:
                    interaction.update_msg('This function is only available to FC members. If you are new, please reach out to any of our admins.')
                else:
                    total_points = DDB_CLIENT.get_member_total_points(member_id, FC_CONFIG.current_submissions_tier)
                    if total_points is None:
                        total_points = 0

                    support_msg = "Get started by doing content with us!"
                    if total_points < 20:
                        "You're off to a great start! Keep it up! :)"
                    elif total_points < 50:
                        "Getting closer! Keep it up!"
                    elif total_points == 50:
                        "Halfway there! You got this!"
                    elif total_points < 80:
                        "Great job! Keep going!"
                    elif total_points < 100:
                        "Almost there! Keep going!"
                    elif total_points >= 100:
                        "**Congratulations!!** :tada:"
                    interaction.update_msg(f'You currently have {total_points} points. {support_msg}')
        # TODO: Implement button callbacks too
    return {
        'statusCode': 200,
        'body': json.dumps({'type': 1})
    }
