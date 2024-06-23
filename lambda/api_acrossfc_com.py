# stdlib
import re
import json
import logging
from typing import List
from decimal import Decimal
from collections.abc import MutableMapping, MutableSequence

# Local
from acrossfc.api import submissions, participation_points
from acrossfc.core.model import Member, PointsCategory
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT
from acrossfc.ext.ddb_client import DDB_CLIENT


RESP_200_JSON = {
    'statusCode': 200,
    'body': 'OK'
}
RESP_404_JSON = {
    'statusCode': 404,
    'body': 'Not found'
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


def lambda_handler(event, context):
    raw_path = event['rawPath']
    PATH = raw_path.split('/')[1:]
    http_method = event['requestContext']['http']['method']
    qs_params = event.get('queryStringParameters', {})
    resp_data = event

    # TODO: Auth

    if PATH[0] == "fc_roster":
        roster: List[Member] = FFLOGS_CLIENT.get_fc_roster()
        resp_data = [
            {
                'member_id': m.fcid,
                'name': m.name,
                'rank': m.rank
            }
            for m in roster
        ]

    if PATH[0] == "current_tier":
        resp_data = submissions.get_current_submissions_tier()

    if PATH[0] == "submissions":
        if http_method == 'GET':
            if len(PATH) == 1:
                # DDB Scan, paginated
                subs = submissions.get_submissions_for_tier(**qs_params)
                resp_data = subs
            elif PATH[1] == "queue":
                queue = submissions.get_submissions_queue()
                resp_data = queue
            elif (m := re.fullmatch(r'^/submissions/([a-zA-Z0-9-]+)$', raw_path)):
                sub_uuid = m.groups()[0]
                sub = DDB_CLIENT.get_submission_by_uuid(sub_uuid)
                resp_data = sub
        elif http_method == 'POST':
            data_str = event.get('body', None)
            data = json.loads(data_str) if data_str is not None else {}
            if PATH[1] == "review":
                resp_data = submissions.review_submission(**data)
            elif PATH[1] == "evaluate":
                eval_results = submissions.evaluate_fflogs(**data)
                resp_data = eval_results
            elif PATH[1] == "fflogs":
                submissions.submit_fflogs(**data)
                resp_data = RESP_200_JSON
            elif PATH[1] == "manual":
                submissions.submit_manual(**data)
                resp_data = RESP_200_JSON

    if PATH[0] == "ppts":
        if http_method == 'GET':
            if len(PATH) == 1:
                resp_data = DDB_CLIENT.get_member_points(**qs_params)
            elif PATH[1] == "leaderboard":
                resp_data = participation_points.get_points_leaderboard(**qs_params)
            elif PATH[1] == "table":
                resp_data = [
                    {
                        'category_id': category.value,
                        'name': category.name,
                        'description': category.description,
                        'constraints': category.constraints,
                        'points': category.points
                    }
                    for category in PointsCategory
                ]

    resp = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(convert_decimals_to_int(resp_data))
    }

    # In prod, return 404
    return resp
