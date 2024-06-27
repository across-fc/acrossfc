# stdlib
from typing import Dict

# 3rd-party
import boto3
from boto3.dynamodb.conditions import Key

# Local
from acrossfc.core.config import FC_CONFIG


class DynamoDBClient:
    def __init__(self):
        self.ddb = boto3.resource('dynamodb')
        self.ppts_table = self.ddb.Table(FC_CONFIG.ddb_participation_points_table)
        self.subs_table = self.ddb.Table(FC_CONFIG.ddb_submissions_table)
        self.subs_q_table = self.ddb.Table(FC_CONFIG.ddb_submissions_queue_table)
        self.members_table = self.ddb.Table(FC_CONFIG.ddb_members_table)

    def get_member_id(self, discord_user_id: int):
        response = self.members_table.query(
            IndexName='discord_user_id-index',
            KeyConditionExpression=Key('discord_user_id').eq(discord_user_id),

        )
        members = response.get('Items', None)
        if len(members) == 0:
            return None
        else:
            return int(members[0]['member_id'])

    def get_member_total_points(self, member_id: int, tier: str):
        response = self.ppts_table.get_item(
            Key={
                'member_id': member_id,
                'tier': tier
            },
            ProjectionExpression='total_points'
        )
        ppt_entry = response.get('Item', None)
        if ppt_entry is None:
            return 0
        return int(ppt_entry['total_points'])

    def get_member_points(self, member_id: int, tier: str):
        response = self.ppts_table.get_item(
            Key={
                'member_id': member_id,
                'tier': tier
            }
        )
        return response.get('Item', None)

    def update_member_points(self, member_points: Dict):
        self.ppts_table.put_item(Item=member_points)

    def get_submission_by_uuid(self, submission_uuid: str):
        response = self.subs_table.get_item(
            Key={
                'uuid': submission_uuid
            }
        )
        return response.get('Item', None)

    def upsert_submission(self, submission: Dict):
        self.subs_table.put_item(Item=submission)

    def upsert_submission_queue_entry(self, submission_queue_entry: Dict):
        self.subs_q_table.put_item(Item=submission_queue_entry)

    def delete_submission_queue_entry(self, submission_uuid: str):
        self.subs_q_table.delete_item(
            Key={
                'uuid': submission_uuid
            }
        )

    def get_points_leaderboard(self, tier: str):
        # TODO: Fix this to only get points for the tier
        response = self.ppts_table.scan(
            ProjectionExpression='member_id, tier, total_points'
        )
        return response.get('Items', None)


DDB_CLIENT = DynamoDBClient()
