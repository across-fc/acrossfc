# stdlib
import os
import json
import boto3
import logging
from typing import List
from datetime import date

# 3rd-party
import requests

# Local
from acrossfc import analytics
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import Clear, Member
from acrossfc.core.constants import TRACKED_ENCOUNTERS
from acrossfc.core.database import ClearDatabase
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT

LOG = logging.getLogger(__name__)


def fc_clears_etl():
    fc_roster: List[Member] = FFLOGS_CLIENT.get_fc_roster()
    fc_clears: List[Clear] = []
    for member in fc_roster:
        fc_clears.extend(
            FFLOGS_CLIENT.get_clears_for_member(member, TRACKED_ENCOUNTERS)
        )

    # Needs to be in /tmp for it to work in Lambda
    cleardb_filename = f"/tmp/{str(date.today())}"
    database = ClearDatabase.from_fflogs(fc_roster, fc_clears)
    database.save(cleardb_filename)

    # Upload ClearDB to S3
    s3 = boto3.client('s3')
    bucket_name = FC_CONFIG.s3_cleardb_bucket_name
    object_key = f'{os.path.basename(cleardb_filename)}'
    s3.upload_file(cleardb_filename, bucket_name, object_key)
    LOG.info(f"{object_key} uploaded successfully")

    # Run clear rates report
    clear_rates_report = analytics.ClearRates(database)

    # Publish clear rates to the FC Discord
    if FC_CONFIG.discord_webhook_url is None:
        LOG.warning(
            "Unable to publish report to Discord webhook. Please configure it in .fcconfig."
        )
    else:
        resp = requests.post(
            FC_CONFIG.discord_webhook_url, data={"content": clear_rates_report.to_discord_str()}
        )
        if resp.status_code != 204:
            raise RuntimeError(
                f"Unable to publish report to Discord webhook URL ({resp.status_code}): {resp.text}"
            )
        LOG.info("Report published to Discord webhook")

    # Publish clear rates to DynamoDB
    TABLE_NAME = FC_CONFIG.ddb_clear_rates_table
    item = {
        'record_date': {'S': 'latest'},
        'value': {
            'S': json.dumps(clear_rates_report.to_dict())
        },
    }
    dynamodb = boto3.client('dynamodb')
    try:
        # Try to update the item
        response = dynamodb.put_item(
            TableName=TABLE_NAME,
            Item=item,
            ConditionExpression='attribute_not_exists(record_date)'
        )
        LOG.debug(f"DynamoDB response: {response}")
        LOG.info("Clear rates inserted successfully")
    except dynamodb.exceptions.ConditionalCheckFailedException:
        # If the item already exists, perform an update
        response = dynamodb.update_item(
            TableName=TABLE_NAME,
            Key={'record_date': {'S': 'latest'}},
            UpdateExpression='SET #attribute_name = :val1',
            # Define the attributes and values to update
            ExpressionAttributeNames={
                '#attribute_name': 'value',
            },
            ExpressionAttributeValues={
                ':val1': item['value'],
            }
        )
        LOG.debug(f"DynamoDB response: {response}")
        LOG.info("Clear rates updated successfully")
    except Exception as e:
        LOG.error(e)
        LOG.info("Error upserting item. Please check the logs for errors.")
