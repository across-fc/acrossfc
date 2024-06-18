# stdlib
import uuid
import time
import logging
from typing import Optional

# 3rd-party
import click
import boto3

# Local
from acrossfc import root_logger
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import PointsEventStatus
from acrossfc.core.points import PointsEvaluator

LOG = logging.getLogger(__name__)


@click.group()
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False,
              help="Turn on verbose logging")
def axs(verbose):
    if verbose:
        root_logger.setLevel(logging.DEBUG)


@axs.command()
@click.option('-i', '--fc-pf-id', required=True)
@click.option('-u', '--fflogs-url')
def submit_fc_pf(fc_pf_id: str, fflogs_url: Optional[str] = None):
    timestamp = int(time.time())
    submission_uuid = str(uuid.uuid4())

    # Get all point events
    point_events = PointsEvaluator(fflogs_url, fc_pf_id).point_events
    point_events_json = [
        {
            'uuid': str(uuid.uuid4()),
            'submission_uuid': submission_uuid,
            'member_id': point_event.member_id,
            'points': point_event.points,
            'category': point_event.category.value,
            'description': f"FC PF: {fc_pf_id}",
            'status': PointsEventStatus.UNAPPROVED.value,
        }
        for point_event in point_events
    ]

    # Upload submission to DDB
    ddb = boto3.resource('dynamodb')
    submissions_table = ddb.Table(FC_CONFIG.ddb_submissions_table)
    submissions_table.put_item(
        Item={
            'uuid': submission_uuid,
            'ts': timestamp,
            'submitted_by': 'bot',   # TODO: FIGURE OUT HOW TO GET USER
            'fc_pf_id': fc_pf_id,
            'fflogs_url': fflogs_url,
            'tier': FC_CONFIG.current_tier,
            'point_events': point_events_json,
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


@axs.command()
def submit_admin():
    # PointsCategory.MENTOR_TICKET: 10,
    # PointsCategory.FC_STATIC: 20,
    # PointsCategory.CRAFTING_GATHERING: 50,
    # PointsCategory.MENTOR: 25
    # PointsCategory.FC_EVENT: 20,
    pass


@axs.command()
def submit():
    # TODO: Mentor tickets?? Can I detect the channel? (10)
    pass
