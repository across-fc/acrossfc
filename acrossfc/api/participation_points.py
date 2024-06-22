# stdlib
from itertools import groupby
from typing import Optional, List, Dict

# 3rd-party
import boto3

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import PointsCategory, PointsEvent


def commit_points_events(points_events: List[PointsEvent], tier: Optional[str] = FC_CONFIG.current_submissions_tier):
    grouped = groupby(points_events, key=lambda pe: pe.member_id)

    for member_id, group in grouped:
        member_points = get_points_for_member(member_id, tier)
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
                member_points['one_time'][pe.category.name] = pe.points
            else:
                member_points['points_events'].append(pe.to_json())
            member_points['total_points'] += pe.points

        _update_member_points(member_points)


def remove_one_time_points(member_id: int, tier: str, category: PointsCategory):
    member_points = get_points_for_member(member_id, tier)
    member_points['total_points'] -= member_points['one_time'][category.name]
    del member_points['one_time'][category.name]
    _update_member_points(member_points)


def remove_points_event(member_id: int, tier: str, point_event_uuid: str):
    member_points = get_points_for_member(member_id, tier)
    for pe in member_points['points_events']:
        if pe['uuid'] == point_event_uuid:
            member_points['total_points'] -= pe['points']
            member_points['points_events'].remove(pe)
            break
    _update_member_points(member_points)


def get_points_for_member(member_id: int, tier: Optional[str] = FC_CONFIG.current_submissions_tier):
    ddb = boto3.resource('dynamodb')
    pp_table = ddb.Table(FC_CONFIG.ddb_participation_points_table)
    response = pp_table.get_item(
        Key={
            'member_id': member_id,
            'tier': tier
        }
    )
    return response.get('Item', None)


def get_points_leaderboard(tier: Optional[str] = FC_CONFIG.current_submissions_tier):
    ddb = boto3.resource('dynamodb')
    pp_table = ddb.Table(FC_CONFIG.ddb_participation_points_table)
    response = pp_table.scan(
        ProjectionExpression='member_id, tier, total_points'
    )
    return response.get('Items', None)


def _update_member_points(member_points: Dict):
    ddb = boto3.resource('dynamodb')
    pp_table = ddb.Table(FC_CONFIG.ddb_participation_points_table)
    pp_table.put_item(Item=member_points)
