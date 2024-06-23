# stdlib
import re
import json
import logging
from typing import List

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


def lambda_handler(event, context):
    raw_path = event['rawPath']
    PATH = raw_path.split('/')[1:]
    http_method = event['requestContext']['http']['method']
    qs_params = event.get('queryStringParameters', {})

    # TODO: Auth
    # TODO: /submissions_queue => /submissions/queue
    # TODO: /review_submissions => /submissions/review

    if PATH[0] == "fc_roster":
        roster: List[Member] = FFLOGS_CLIENT.get_fc_roster()
        return [
            {
                'member_id': m.fcid,
                'name': m.name,
                'rank': m.rank
            }
            for m in roster
        ]

    if PATH[0] == "current_tier":
        return submissions.get_current_submissions_tier()

    if PATH[0] == "submissions":
        if http_method == 'GET':
            if len(PATH) == 1:
                # DDB Scan, paginated
                subs = submissions.get_submissions_for_tier(**qs_params)
                return subs
            elif PATH[1] == "queue":
                queue = submissions.get_submissions_queue()
                return queue
            elif (m := re.fullmatch(r'^/submissions/([a-zA-Z0-9-]+)$', raw_path)):
                sub_uuid = m.groups()[0]
                sub = DDB_CLIENT.get_submission_by_uuid(sub_uuid)
                return sub
        elif http_method == 'POST':
            data_str = event.get('body', None)
            data = json.loads(data_str) if data_str is not None else {}
            if PATH[1] == "review":
                return submissions.review_submission(**data)
            elif PATH[1] == "evaluate":
                eval_results = submissions.evaluate_fflogs(**data)
                return eval_results
            elif PATH[1] == "fflogs":
                # TODO:
                logging.info("Not implemented yet.")
                return RESP_200_JSON
            elif PATH[1] == "manual":
                submissions.submit_manual(**data)
                return RESP_200_JSON

    if PATH[0] == "ppts":
        if http_method == 'GET':
            if len(PATH) == 1:
                return DDB_CLIENT.get_member_points(**qs_params)
            elif PATH[1] == "leaderboard":
                return participation_points.get_points_leaderboard(**qs_params)
            elif PATH[1] == "table":
                return [
                    {
                        'category_id': category.value,
                        'name': category.name,
                        'description': category.description,
                        'constraints': category.constraints,
                        'points': category.points
                    }
                    for category in PointsCategory
                ]

    # In prod, return 404
    return event
