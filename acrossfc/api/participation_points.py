# stdlib
import logging
from itertools import groupby
from typing import Optional, List

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import PointsCategory, PointsEvent, PointsEventStatus
from acrossfc.api.fc_roster import get_member_id_by_name
from acrossfc.ext.ddb_client import DDB_CLIENT

LOG = logging.getLogger(__name__)


def commit_member_points_events(
    points_events: List[PointsEvent],
    tier: str
):
    grouped = groupby(points_events, key=lambda pe: pe.member_id)

    for member_id, group in grouped:
        member_points = DDB_CLIENT.get_member_points(tier, member_id)
        if member_points is None:
            member_points = {
                'member_id': member_id,
                'tier': tier,
                'total_points': 0,
                'one_time': {},
                'points_events': []
            }
        for pe in group:
            if pe.category.is_one_time:
                if pe.category.name in member_points['one_time']:
                    pe.status = PointsEventStatus.ONE_TIME_POINTS_ALREADY_AWARDED
                else:
                    member_points['one_time'][pe.category.name] = pe.to_user_json()
                    member_points['total_points'] += pe.points
            else:
                member_points['points_events'].append(pe.to_user_json())
                member_points['total_points'] += pe.points

        DDB_CLIENT.update_member_points(member_points)


def remove_points_events(tier: str, member_id: int, pe_uuid_list: List[str]):
    print(pe_uuid_list)
    member_points = DDB_CLIENT.get_member_points(tier, member_id)
    if member_points is None:
        LOG.warn(f"Trying to remove tier {tier} points from member {member_id} that does not have a PPTS entry.")
        return

    # Check regular points events
    for i, pe in enumerate(member_points['points_events']):
        if pe['uuid'] in pe_uuid_list:
            del member_points['points_events'][i]
            member_points['total_points'] -= pe['points']

    # Check one-time points events
    for category in member_points['one_time']:
        # otpe: One-time points event
        otpe = member_points['one_time'][category]['uuid']
        if otpe['uuid'] in pe_uuid_list:
            del member_points['one_time'][category]
            member_points['total_points'] -= pe['points']

    DDB_CLIENT.update_member_points(member_points)


def get_points_for_member(tier: str, member_id: int):
    return DDB_CLIENT.get_member_points(tier, member_id)


def get_points_for_member_by_name(tier: str, member_name: str):
    member_id = get_member_id_by_name(member_name)
    if member_id is None:
        return None
    return DDB_CLIENT.get_member_points(tier, member_id)


def remove_one_time_points(tier: str, member_id: int, category: PointsCategory):
    member_points = DDB_CLIENT.get_member_points(tier, member_id)
    if category.name not in member_points['one_time']:
        LOG.info(f"Member {member_id} does not have {category.name} one-time points. Nothing to remove.")
        return

    member_points['total_points'] -= member_points['one_time'][category.name]['points']
    del member_points['one_time'][category.name]
    DDB_CLIENT.update_member_points(member_points)


def remove_points_event(member_id: int, tier: str, point_event_uuid: str):
    member_points = DDB_CLIENT.get_member_points(tier, member_id)
    for pe in member_points['points_events']:
        if pe['uuid'] == point_event_uuid:
            member_points['total_points'] -= pe['points']
            member_points['points_events'].remove(pe)
            DDB_CLIENT.update_member_points(member_points)
            break


def get_points_leaderboard(tier: Optional[str] = FC_CONFIG.current_submissions_tier):
    return DDB_CLIENT.get_points_leaderboard(tier)
