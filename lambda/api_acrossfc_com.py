# stdlib
import os
import re
import json
from decimal import Decimal
from collections.abc import MutableMapping, MutableSequence

# Local
from acrossfc import root_logger as LOG
from acrossfc.api import submissions, participation_points, fc_roster
from acrossfc.core.model import PointsCategory
from acrossfc.ext.ddb_client import DDB_CLIENT


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
    resp_data = None

    # TODO: Auth


    if PATH[0] == "fc_roster":
        resp_data = fc_roster.get_fc_roster()

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
                resp_data = {}
            elif PATH[1] == "manual":
                submissions.submit_manual(**data)
                resp_data = {}

    if PATH[0] == "ppts":
        if http_method == 'GET':
            if len(PATH) == 1:
                if 'member_id' in qs_params:
                    # TODO: Figure out a cleaner solution
                    qs_params['member_id'] = int(qs_params['member_id'])
                    resp_data = participation_points.get_points_for_member(**qs_params)
                elif 'member_name' in qs_params:
                    resp_data = participation_points.get_points_for_member_by_name(**qs_params)
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

    if resp_data is None:
        statusCode = 404
        if os.environ.get('AX_ENV') == "TEST":
            resp_data = event
    else:
        statusCode = 200

    resp = {
        'statusCode': statusCode,
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
