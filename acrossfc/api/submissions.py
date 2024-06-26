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


def evaluate_fflogs(
    fflogs_url: str,
    is_fc_pf: bool,
    is_static: bool,
    fc_pf_id: Optional[str] = None
):
    # TODO: Change this to return a submissions object
    # Get all point events
    points_events = PointsEvaluator(fflogs_url, is_fc_pf, is_static, fc_pf_id).points_events
    return [
        pe.to_submission_json()
        for pe in points_events
    ]


def submit_manual(
    point_categories_to_member_ids_map: Dict[PointsCategoryLike, List[int]],
    submitted_by: ComboUserID,
    submission_channel: SubmissionsChannelLike,
    is_static: bool,
    is_fc_pf: bool,
    fflogs_url: Optional[str] = None,
    fc_pf_id: Optional[str] = None,
    auto_approve_admin_id: Optional[int] = None,
    notes: Optional[str] = None
):
    """
    Manual submission of points, most likely by an admin from the admin portal.

    In this method, we do not parse the FFLogs URL, and we assume all points will be given to us as inputs.
    The fflogs_url input is just for tracking.

    Similarly, we do not automatically add points events for FC PF if fc_pf_id is given.
    """
    auto_approve = auto_approve_admin_id is not None
    if auto_approve and auto_approve_admin_id not in FC_CONFIG.fc_admin_ids:
        raise ValueError(f"{auto_approve_admin_id} is not a recognized admin ID.")

    submission_uuid = str(uuid.uuid4())
    submission_channel = SubmissionsChannel.to_enum(submission_channel)

    points_events = []
    for pc in point_categories_to_member_ids_map:
        member_ids = point_categories_to_member_ids_map[pc]

        pc = PointsCategory.to_enum(pc)
        for member_id in member_ids:
            points_events.append(PointsEvent(
                uuid=str(uuid.uuid4()),
                member_id=member_id,
                points=pc.points,
                category=pc,
                description=f"{pc.name} (Manual)",
                ts=int(time.time()),
                submission_uuid=submission_uuid,
                status=(PointsEventStatus.APPROVED if auto_approve else PointsEventStatus.PENDING)
            ))

    # Note: The order of operations is important here.
    # First try to commit member points and catch any dedupes, then add the submission, then add to queue if necessary.
    timestamp = int(time.time())
    last_update_ts = None
    last_update_by = None

    if auto_approve:
        commit_member_points_events(points_events, tier=FC_CONFIG.current_submissions_tier)
        last_update_ts = timestamp
        last_update_by = auto_approve_admin_id

    DDB_CLIENT.upsert_submission({
        'uuid': submission_uuid,
        'ts': timestamp,
        'submitted_by': submitted_by,
        'submission_channel': submission_channel.value,
        'is_ic_pf': is_fc_pf,
        'is_static': is_static,
        'fc_pf_id': fc_pf_id,
        'fflogs_url': fflogs_url,
        'tier': FC_CONFIG.current_submissions_tier,
        'points_events': [pe.to_submission_json() for pe in points_events],
        'last_update_ts': last_update_ts,
        'last_update_by': last_update_by,
        'notes': notes
    })

    if not auto_approve:
        DDB_CLIENT.upsert_submission_queue_entry({
            'uuid': submission_uuid,
            'ts': timestamp
        })


def submit_fflogs(
    fflogs_url: str,
    submitted_by: ComboUserID,
    submission_channel: SubmissionsChannelLike,
    is_static: bool,
    is_fc_pf: bool,
    fc_pf_id: Optional[str] = None,
):
    submission_channel = SubmissionsChannel.to_enum(submission_channel)
    timestamp = int(time.time())

    # Get all point events
    points_events: List[PointsEvent] = PointsEvaluator(fflogs_url, is_fc_pf, is_static, fc_pf_id).points_events

    if len(points_events) == 0:
        LOG.info("No points were awarded for this fight.")

    points_events_json = [pe.to_submission_json() for pe in points_events]

    # Upload submission to DDB
    submission_uuid = str(uuid.uuid4())
    DDB_CLIENT.upsert_submission({
        'uuid': submission_uuid,
        'ts': timestamp,
        'submitted_by': submitted_by,
        'submission_channel': submission_channel.value,
        'is_ic_pf': is_fc_pf,
        'is_static': is_static,
        'fc_pf_id': fc_pf_id,
        'fflogs_url': fflogs_url,
        'tier': FC_CONFIG.current_submissions_tier,
        'points_events': points_events_json,
        'last_update_ts': None,
        'last_update_by': None,
        'notes': None
    })
    DDB_CLIENT.upsert_submission_queue_entry({
        'uuid': submission_uuid,
        'ts': timestamp
    })
    LOG.info(f"Inserted submission {submission_uuid} into DynamoDB.")


def review_submission(
    submission_uuid: str,
    points_event_to_approved: Dict[str, bool],
    reviewer_id: int,
    notes: Optional[str] = None
):
    submission = DDB_CLIENT.get_submission_by_uuid(submission_uuid)

    # Add all approved points for member
    user_points_events_to_commit: List[PointsEvent] = []
    for pe in submission['points_events']:
        pe_approved = points_event_to_approved[pe['uuid']]
        pe_status = PointsEventStatus.APPROVED if pe_approved else PointsEventStatus.DENIED
        pe['status'] = pe_status.value
        if pe_approved:
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
    submission['last_update_by'] = reviewer_id
    submission['notes'] = notes

    DDB_CLIENT.upsert_submission(submission)
    DDB_CLIENT.delete_submission_queue_entry(submission_uuid)

    return None
