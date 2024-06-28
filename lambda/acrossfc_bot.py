import re
import json
import logging

# Local
from acrossfc import ANALYTICS_LOG
from acrossfc.core.config import FC_CONFIG
from acrossfc.api.submissions import SubmissionsChannel, submit_fflogs
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


def show_fc_points_options(interaction: Interaction, discord_user_id):
    interaction.respond(
        msg="What would you like to do?",
        components=[
            {
                "type": 1,
                "components": [
                    {
                        "type": 3,
                        "custom_id": "fc_points_select",
                        "options": [
                            {
                                "label": "Submit FFLogs report",
                                "description": "Earn FC participation points by doing content!",
                                "value": "submit_ppts"
                            },
                            {
                                "label": "Check my points",
                                "description": "See how many points you have earned so far this tier!",
                                "value": "check_ppts"
                            }
                        ],
                        "placeholder": "Choose an action:"
                    }
                ]
            }
        ],
        ephemeral=True
    )


def handle_check_fc_points_selection(interaction, discord_user_id):
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
                support_msg = "You're off to a great start! Keep it up! :)"
            elif total_points < 50:
                support_msg = "Getting closer! Keep it up!"
            elif total_points == 50:
                support_msg = "Halfway there! You got this!"
            elif total_points < 80:
                support_msg = "Great job! Keep going!"
            elif total_points < 100:
                support_msg = "Almost there! Keep going!"
            elif total_points >= 100:
                support_msg = "**Congratulations!!** :tada:"
            interaction.update_msg(f'You currently have {total_points} points. {support_msg}')


def handle_submit_fflogs_selection(interaction: Interaction, discord_user_id):
    interaction.modal(
        custom_id='submit_fflogs_modal',
        title='Submit FFLogs Report',
        components=[
            {
                "type": 1,
                "components": [
                    {
                        "type": 4,
                        "custom_id": "fflogs_url_input",
                        "label": "FFLogs URL",
                        "placeholder": "URL must include '/report/<code>' and 'fight=##'",
                        "style": 1,
                        "min_length": 32,
                        "max_length": 512,
                        "required": True
                    }
                ]
            }
        ]
    )


INVALID_FFLOGS_URL_MSG = """
:warning: **Invalid FFLogs URL**

Make sure the URL has `/reports/<code>#fight=<id>` in it.
"""
SUBMISSION_SUCCESSFUL_MSG = """
<a:FCApplicationsCheck:820783050308321280> **Logs submitted**

Any available points will be awarded within 48 hours. In the meantime, you can use `/fc_points` to see how many points you have.
""" 
SUBMISSION_ERROR_MSG = """
:warning: **Server Error**

Something went wrong while trying to submit your log.

Please contact <@795916443891531786> immediately.
"""


def handle_submit_fflogs_submission(body, interaction: Interaction, discord_user_id):
    interaction.thinking()
    fflogs_url = body['data']['components'][0]['components'][0]['value']
    if not re.match(r'.*reports/([a-zA-Z0-9]+)#fight=([0-9]+)', fflogs_url):
        interaction.update_msg(INVALID_FFLOGS_URL_MSG)
    else:
        try:
            submit_fflogs(fflogs_url, {
                'discord_user_id': discord_user_id,
                'discord_server_name': body['member']['nick'],
                'discord_global_name': body['member']['user']['global_name']
            }, SubmissionsChannel.FC_BOT_FFLOGS, False, False, None)
            interaction.update_msg(SUBMISSION_SUCCESSFUL_MSG)
        except Exception as e:
            logging.error(f"[INTERACTION ID: {interaction.interaction_id}] Exception while submitting FFLogs: {e}")
            interaction.update_msg(SUBMISSION_ERROR_MSG + f"\n(IID: {interaction.interaction_id})")


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
    interaction_id = body['id']
    interaction_token = body['token']
    interaction = Interaction(interaction_id, interaction_token)
    discord_user_id = body['member']['user']['id'] if 'member' in body else body['user']['id']

    if body['type'] == 2:
        # Application commands (Slash commands)
        command_name = body['data']['name']
        ANALYTICS_LOG.info(f"{discord_user_id} {command_name}")
        if command_name == "fc_points":
            show_fc_points_options(interaction, discord_user_id)
            interaction.delete_original_msg(15)
    elif body['type'] == 3:
        # Message component (Buttons)
        custom_id = body['data']['custom_id']
        ANALYTICS_LOG.info(f"{discord_user_id} {custom_id}")

        if custom_id == 'fc_points_button':
            show_fc_points_options(interaction, discord_user_id)
            interaction.delete_original_msg(15)
        elif custom_id == 'fc_points_select':
            selected_value = body['data']['values'][0]
            if selected_value.startswith('check_ppts'):
                handle_check_fc_points_selection(interaction, discord_user_id)
            elif any(v.startswith("submit_ppts") for v in body['data']['values']):
                handle_submit_fflogs_selection(interaction, discord_user_id)
        else:
            logging.warn(f"Unidentified custom_id type: {custom_id}")
    elif body['type'] == 5:
        ANALYTICS_LOG.info(f"{discord_user_id} submit_fflogs_modal")
        handle_submit_fflogs_submission(body, interaction, discord_user_id)

    return {
        'statusCode': 200,
        'body': json.dumps({'type': 1})
    }
