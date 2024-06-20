# stdlib
import uuid
import time
import logging
from typing import Optional, Any, Dict

# 3rd-party
import boto3
from boto3.dynamodb.conditions import Key

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import PointsEventStatus
from acrossfc.core.points import PointsEvaluator
from .participation_points import add_points

LOG = logging.getLogger(__name__)


def get_submissions_for_tier(
    tier: str = FC_CONFIG.current_submissions_tier,
    exclusive_start_key: Optional[Any] = None
):
    ddb = boto3.resource('dynamodb')
    submissions_table = ddb.Table(FC_CONFIG.ddb_submissions_table)
    query_args = {
        'IndexName': 'tier-ts-index',
        'KeyConditionExpression': Key('tier').eq(tier),
        'ScanIndexForward': False,
    }
    if exclusive_start_key is not None:
        query_args['ExclusiveStartKey'] = exclusive_start_key

    response = submissions_table.query(**query_args)

    return {
        'items': response['Items'],
        'count': response['Count'],
        'lastEvalutedKey': response.get('LastEvaluatedKey', None)
    }


def get_submissions_by_uuid(_uuid: str):
    ddb = boto3.resource('dynamodb')
    submissions_table = ddb.Table(FC_CONFIG.ddb_submissions_queue_table)
    return submissions_table.get_item(
        Key={
            'uuid': _uuid
        }
    ).get('Item', {})


def get_submissions_queue(exclusive_start_key: Optional[Any] = None):
    ddb = boto3.resource('dynamodb')
    submissions_table = ddb.Table(FC_CONFIG.ddb_submissions_queue_table)

    if exclusive_start_key is not None:
        response = submissions_table.scan(ExclusiveStartKey=exclusive_start_key)
    else:
        response = submissions_table.scan()

    return {
        'items': response['Items'],
        'count': response['Count'],
        'lastEvalutedKey': response.get('LastEvaluatedKey', None)
    }


def get_current_submissions_tier():
    return FC_CONFIG.current_submissions_tier


def submit_fc_pf(fc_pf_id: str, fflogs_url: Optional[str] = None):
    timestamp = int(time.time())

    # Get all point events
    points_events = PointsEvaluator(fflogs_url, fc_pf_id).points_events
    points_events_json = [
        {
            'uuid': str(uuid.uuid4()),
            'member_id': points_event.member_id,
            'points': points_event.points,
            'category': points_event.category.value,
            'description': points_event.description,
            'status': PointsEventStatus.UNAPPROVED.value,
        }
        for points_event in points_events
    ]

    # Upload submission to DDB
    ddb = boto3.resource('dynamodb')
    submission_uuid = str(uuid.uuid4())
    submissions_table = ddb.Table(FC_CONFIG.ddb_submissions_table)
    submissions_table.put_item(
        Item={
            'uuid': submission_uuid,
            'ts': timestamp,
            'submitted_by': 'bot',   # TODO: FIGURE OUT HOW TO GET USER
            'fc_pf_id': fc_pf_id,
            'fflogs_url': fflogs_url,
            'tier': FC_CONFIG.current_submissions_tier,
            'points_events': points_events_json,
            'last_update_ts': None,
            'last_update_by': None,
        }
    )
    submissions_queue_table = ddb.Table(FC_CONFIG.ddb_submissions_queue_table)
    submissions_queue_table.put_item(
        Item={
            'uuid': submission_uuid,
            'ts': timestamp
        }
    )
    LOG.info(f"Inserted submission {submission_uuid} into DynamoDB.")


def review_submission(
    submission_uuid: str,
    points_event_to_approval_status: Dict[str, PointsEventStatus],
    reviewer_id: int
):
    submission = get_submissions_by_uuid(submission_uuid)

    # Add all approved points to user
    for points_event in submission['points_events']:
        points_event['status'] = points_event_to_approval_status[points_event['uuid']].value
        if points_event['status'] == PointsEventStatus.APPROVED:
            # TODO: Implement
            add_points()

    submission['last_update_ts'] = int(time.time())
    submission['last_update_by'] = reviewer_id

    # Update submission entry
    ddb = boto3.resource('dynamodb')
    submissions_table = ddb.Table(FC_CONFIG.ddb_submissions_table)
    submissions_table.put_item(Item=submission)

    # Delete submission queue entry
    submissions_queue_table = ddb.Table(FC_CONFIG.ddb_submissions_queue_table)
    submissions_queue_table.delete_item(
        Key={
            'uuid': submission_uuid
        }
    )
