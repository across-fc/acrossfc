# stdlib
from typing import Optional, List

# 3rd-party
import boto3

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import PointsCategory, PointsEvent


def add_points(points_events: List[PointsEvent]):
    # PointsCategory.MENTOR_TICKET: 10,
    # PointsCategory.FC_STATIC: 20,
    # PointsCategory.CRAFTING_GATHERING: 50,
    # PointsCategory.MENTOR: 25
    # PointsCategory.FC_EVENT: 20,
    pass


# TODO: Remove point event for member
def remove_points(member_id: int, point_event_uuid: Optional[str], one_time_points_category: PointsCategory):
    pass


def add_user(member_id: int, tier: Optional[str] = FC_CONFIG.current_submissions_tier):
    ddb = boto3.resource('dynamodb')
    pp_table = ddb.Table(FC_CONFIG.ddb_participation_points_table)
    pp_table.put_item(
        Item={
            'member_id': member_id,
            'tier': tier,
            'one_time': {},
            'points_events': []
        }
    )
