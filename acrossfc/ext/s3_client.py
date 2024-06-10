import os
import logging

# 3rd-party
import boto3

# Local
from acrossfc.core.config import FC_CONFIG

LOG = logging.getLogger(__name__)


def upload_clear_database(local_db_file: str):
    s3 = boto3.client('s3')
    bucket_name = FC_CONFIG.s3_db_backup_bucket_name
    object_key = f'database/{os.path.basename(local_db_file)}'
    try:
        s3.upload_file(local_db_file, bucket_name, object_key)
        LOG.info(f"{object_key} uploaded successfully")
    except Exception as e:
        LOG.error(f"Error uploading {object_key}: {e}")
