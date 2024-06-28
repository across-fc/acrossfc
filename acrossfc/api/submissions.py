# stdlib
import uuid
import time
import logging
from typing import Optional, Any, Dict, List, Union

# 3rd-party
import boto3
from boto3.dynamodb.conditions import Key

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import (
    PointsEvent,
    PointsEventStatus,
    PointsCategory,
    SubmissionsChannel
)
from acrossfc.core.points_evaluator import PointsEvaluator
from acrossfc.ext.ddb_client import DDB_CLIENT
from .participation_points import commit_member_points_events

LOG = logging.getLogger(__name__)

PointsCategoryLike = Union[PointsCategory, int, str]
SubmissionsChannelLike = Union[SubmissionsChannel, int, str]
ComboUserID = Dict[str, Union[int, str]]


def get_submissions_for_tier(
    tier: str = FC_CONFIG.current_submissions_tier,
    exclusive_start_key: Optional[Any] = None
):
    # TODO: Iteratively get all, move to DDB_CLIENT
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


def get_submissions_queue(exclusive_start_key: Optional[Any] = None):
    # TODO: Iteratively get all, move to DDB_CLIENT
    ddb = boto3.resource('dynamodb')
    submissions_table = ddb.Table(FC_CONFIG.ddb_submissions_queue_table)

    if exclusive_start_key is not None:
        response = submissions_table.scan(ExclusiveStartKey=exclusive_start_key)
    else:
        response = submissions_table.scan()

    data = {
        'items': response['Items'],
        'count': response['Count'],
        'lastEvalutedKey': response.get('LastEvaluatedKey', None)
    }
    return data


def get_current_submissions_tier():
    return FC_CONFIG.current_submissions_tier


def submit_fflogs(
    fflogs_url: str,
    submitted_by: ComboUserID,
    submission_channel: SubmissionsChannelLike,
    is_static: bool,
    is_fc_pf: bool,
    fc_pf_id: Optional[str] = None,
    notes: Optional[str] = None,
    eval_mode: bool = False
):
    submission_channel = SubmissionsChannel.to_enum(submission_channel)
    timestamp = int(time.time())

    # Get all point events
    evaluator = PointsEvaluator(fflogs_url, is_fc_pf, is_static, fc_pf_id)
    points_events: List[PointsEvent] = evaluator.points_events
    fight_signature: int = evaluator.fight_data.fight_signature

    if len(points_events) == 0:
        LOG.info("No points were awarded for this fight.")

    points_events_json = [pe.to_submission_json() for pe in points_events]

    # Upload submission to DDB
    submission_uuid = str(uuid.uuid4())
    submission = {
        'uuid': submission_uuid,
        'ts': timestamp,
        'submitted_by': submitted_by,
        'submission_channel': submission_channel.value,
        'is_fc_pf': is_fc_pf,
        'is_static': is_static,
        'fc_pf_id': fc_pf_id,
        'fflogs_url': fflogs_url,
        'fight_signature': fight_signature,
        'tier': FC_CONFIG.current_submissions_tier,
        'points_events': points_events_json,
        'last_update_ts': None,
        'last_update_by': None,
        'notes': notes
    }

    if not eval_mode:
        DDB_CLIENT.upsert_submission(submission)
        DDB_CLIENT.upsert_submission_queue_entry({
            'uuid': submission_uuid,
            'ts': timestamp
        })
        LOG.info(f"Inserted submission {submission_uuid} into DynamoDB.")

    return submission


def review_submission(submission):
    # Add all approved points for member
    user_points_events_to_commit: List[PointsEvent] = []
    for pe in submission['points_events']:
        if pe['status'] == PointsEventStatus.APPROVED.value:
            user_points_events_to_commit.append(PointsEvent(
                uuid=pe['uuid'],
                member_id=pe['member_id'],
                points=pe['points'],
                category=PointsCategory.to_enum(pe['category']),
                description=pe['description'],
                ts=pe['ts'],
                submission_uuid=submission['uuid'],
                status=PointsEventStatus.APPROVED
            ))

    commit_member_points_events(user_points_events_to_commit, tier=submission['tier'])

    # Update points event statuses based on the commit result
    updated_points_event_status: Dict[str, PointsEventStatus] = {
        pe.uuid: pe.status
        for pe in user_points_events_to_commit
    }
    for pe in submission['points_events']:
        if pe['uuid'] in updated_points_event_status:
            pe['status'] = updated_points_event_status[pe['uuid']].value

    submission['last_update_ts'] = int(time.time())

    DDB_CLIENT.upsert_submission(submission)
    DDB_CLIENT.delete_submission_queue_entry(submission['uuid'])

    return None
