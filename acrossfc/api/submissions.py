# stdlib
import uuid
import time
import logging
from typing import Optional, Any, Dict, List

# 3rd-party
import boto3
from boto3.dynamodb.conditions import Key

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import PointsEvent, PointsCategory, SubmissionsChannel
from acrossfc.core.points_evaluator import PointsEvaluator
from .participation_points import commit_points_events

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
    submissions_table = ddb.Table(FC_CONFIG.ddb_submissions_table)
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


def analyze_fflogs(fflogs_url: str, fc_pf_id: Optional[str] = None):
    # Get all point events
    points_events = PointsEvaluator(fflogs_url, fc_pf_id).points_events
    return [
        pe.to_json()
        for pe in points_events
    ]


def submit_manual(category: PointsCategory | int | str, member_ids: List[int]):
    category = PointsCategory.to_enum(category)
    # TODO: Implement
    pass


def submit_fflogs(
    fflogs_url: str,
    submitted_by_name: str,
    submission_channel: SubmissionsChannel | int | str,
    fc_pf_id: Optional[str] = None,
):
    submission_channel = SubmissionsChannel.to_enum(submission_channel)
    timestamp = int(time.time())

    # Get all point events
    points_events = PointsEvaluator(fflogs_url, fc_pf_id).points_events

    if len(points_events) == 0:
        LOG.info("No points were awarded for this fight.")

    points_events_json = [
        {
            'uuid': points_event.uuid,
            'member_id': points_event.member_id,
            'points': points_event.points,
            'category': points_event.category.value,
            'description': points_event.description,
            'ts': points_event.ts,
            'approved': None
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
            'submitted_by': submitted_by_name,
            'submission_channel': submission_channel.value,
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
    points_event_to_approved: Dict[str, bool],
    reviewer_id: int,
    notes: Optional[str] = None
):
    submission = get_submissions_by_uuid(submission_uuid)

    # Add all approved points to user
    points_events_to_add: List[PointsEvent] = []
    for pe in submission['points_events']:
        pe['approved'] = points_event_to_approved[pe['uuid']]
        if pe['approved']:
            points_events_to_add.append(PointsEvent(
                uuid=pe['uuid'],
                member_id=pe['member_id'],
                points=pe['points'],
                category=PointsCategory(pe['category']),
                description=pe['description'],
                ts=pe['ts'],
                submission_uuid=submission['uuid'],
                fc_pf_id=submission.get('fc_pf_id', None),
                approved=True,
                reviewed_by=reviewer_id,
            ))

    commit_points_events(points_events_to_add)

    submission['last_update_ts'] = int(time.time())
    submission['last_update_by'] = reviewer_id
    submission['notes'] = notes

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

    return None
