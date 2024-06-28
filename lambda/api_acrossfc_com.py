# stdlib
import os
import re
import json
import hmac
import hashlib
import requests
from typing import Optional, Dict
from decimal import Decimal
from collections.abc import MutableMapping, MutableSequence

# Local
from acrossfc import ROOT_LOG as LOG
from acrossfc.api import submissions, participation_points, fc_roster
from acrossfc.core.model import PointsCategory
from acrossfc.core.config import FC_CONFIG
from acrossfc.ext.ddb_client import DDB_CLIENT

ALLOWED_HEADER_NAMES = [
    'Content-Type',
    'X-Amz-Date',
    'Authorization',
    'X-Api-Key',
    'X-Amz-Security-Token',
    'X-AX-DACCESS-TOKEN',
    'X-AX-DBOT-TOKEN'
]
COMMON_HEADERS = {
    'Access-Control-Allow-Headers': ','.join(ALLOWED_HEADER_NAMES),
    'Access-Control-Allow-Origin': FC_CONFIG.cors_allow_origin,
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}


def response(status_code: int, msg: Optional[str] = None, data: Optional[Dict] = None):
    body = msg
    headers = COMMON_HEADERS
    if data is not None:
        body = json.dumps(convert_decimals_to_int(data))
        headers = COMMON_HEADERS | {'Content-Type': 'application/json'}

    return {
        'statusCode': status_code,
        'headers': headers,
        'body': body
    }


def convert_decimals_to_int(obj):
    """
    Recursively converts all Decimal instances in a given object to integers.
    """
    if isinstance(obj, MutableMapping):  # If obj is a dictionary
        return {k: convert_decimals_to_int(v) for k, v in obj.items()}
    elif isinstance(obj, MutableSequence):  # If obj is a list
        return [convert_decimals_to_int(i) for i in obj]
    elif isinstance(obj, Decimal):  # If obj is a Decimal
        return int(obj)
    else:
        return obj


def verify_bot_signature(data, signature) -> bool:
    expected_signature = hmac.new(
        FC_CONFIG.il_palazzo_key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature == expected_signature


def lambda_handler(event, context):
    http_method = event['requestContext']['http']['method']
    if http_method == 'OPTIONS':
        return response(204)

    raw_path = event['rawPath']
    PATH = raw_path.split('/')[1:]
    qs_params = event.get('queryStringParameters', {})

    # BEGIN Auth ------------------------
    if 'x-ax-daccess-token' in event['headers']:
        token = f"Bearer {event['headers']['x-ax-daccess-token']}"
        d_resp = requests.get("https://discord.com/api/v10/users/@me", headers={
            'Authorization': token
        })
        if d_resp.status_code != 200:
            LOG.error(f"Error while trying to authorize with Discord. {d_resp.text}")
            return response(401)

        discord_id = d_resp.json()['id']
        discord_name = d_resp.json()['username']
        if discord_id not in FC_CONFIG.allowed_discord_id_list:
            LOG.warn(f"Discord user {discord_name} ({discord_id}) tried to access the API.")
            return response(403)
    elif 'x-ax-bot-signature' in event['headers']:
        if not verify_bot_signature(event['body'], event['headers']['x-ax-bot-signature']):
            LOG.warn(f"Failed to verify bot signature. Request rejected. {event}")
            return response(403)
    else:
        return response(401)

    # END Auth ------------------------

    if PATH[0] == "fc_roster":
        data = fc_roster.get_fc_roster()
        return response(200, data=data)

    if PATH[0] == "current_tier":
        data = submissions.get_current_submissions_tier()
        return response(200, data=data)

    if PATH[0] == "submissions":
        if http_method == 'GET':
            if len(PATH) == 1:
                # DDB Scan, paginated
                subs = submissions.get_submissions_for_tier(**qs_params)
                return response(200, data=subs)
            elif PATH[1] == "queue":
                queue = submissions.get_submissions_queue()
                return response(200, data=queue)
            elif (m := re.fullmatch(r'^/submissions/([a-zA-Z0-9-]+)$', raw_path)):
                sub_uuid = m.groups()[0]
                sub = DDB_CLIENT.get_submission_by_uuid(sub_uuid)
                return response(200, data=sub)
        elif http_method == 'POST':
            data_str = event.get('body', None)
            data = json.loads(data_str) if data_str is not None else {}
            if PATH[1] == "review":
                data = submissions.review_submission(**data)
                return response(200, data=data)
            elif PATH[1] == "evaluate":
                eval_results = submissions.evaluate_fflogs(**data)
                return response(200, data=eval_results)
            elif PATH[1] == "fflogs":
                submissions.submit_fflogs(**data)
                return response(200)
            elif PATH[1] == "manual":
                submissions.submit_manual(**data)
                return response(200)

    if PATH[0] == "ppts":
        if http_method == 'GET':
            if len(PATH) == 1:
                if 'member_id' in qs_params:
                    # TODO: Figure out a cleaner solution
                    qs_params['member_id'] = int(qs_params['member_id'])
                    data = participation_points.get_points_for_member(**qs_params)
                    return response(200, data=data)
            elif PATH[1] == "leaderboard":
                data = participation_points.get_points_leaderboard(**qs_params)
                return response(200, data=data)
            elif PATH[1] == "table":
                data = [
                    {
                        'category_id': category.value,
                        'name': category.name,
                        'description': category.description,
                        'constraints': category.constraints,
                        'points': category.points
                    }
                    for category in PointsCategory
                ]
                return response(200, data=data)

    data = None
    if os.environ.get('AX_ENV') == "TEST":
        data = event

    return response(404, data=data)
