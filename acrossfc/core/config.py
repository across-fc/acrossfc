# stdlib
import os
import logging
import configparser

# Local
from acrossfc import ENV

LOG = logging.getLogger(__name__)


class FCConfig:
    """
    Loads FC configs from a file.

    Expected structure:

        [DEFAULT]
        FFLogsGuildID = #####
        ExcludeGuildRanks = #,##,...    (optional)
        DiscordWebhookURL = ...         (optional)

    """
    def __init__(self, fc_config_filename: str, env: str):
        self.fc_config_filename = fc_config_filename
        self.env = env

        configs = configparser.ConfigParser()
        configs.read(fc_config_filename)
        default_configs = configs["DEFAULT"]
        if env not in configs:
            raise ValueError(f"Environment {env} not found in FC config file ({self.fc_config_filename}).")
        default_configs.update(configs[env])
        self.combined_configs = default_configs

        # Assert we have FFLogs client credentials
        fflogs_client_id = default_configs.get("fflogs_client_id", None)
        fflogs_client_secret = default_configs.get("fflogs_client_secret", None)
        if fflogs_client_id is None or fflogs_client_secret is None:
            raise RuntimeError(
                f'fflogs_client_id or fflogs_client_secret are missing from {fc_config_filename}.'
            )

        # Parse FFLogs guild ID
        self.fflogs_guild_id = int(default_configs.get("fflogs_guild_id", -1))
        if self.fflogs_guild_id == -1:
            raise RuntimeError(
                f'fflogs_guild_id is missing from {fc_config_filename}.'
            )

        # Parse guild ranks to exclude
        exclude_guild_ranks_str = default_configs.get("exclude_guild_ranks", "")
        self.exclude_guild_ranks = set(
            int(s.strip())
            for s in exclude_guild_ranks_str.split(",")
            if s.strip() != ""
        )

        # Get S3 database file backup name
        self.s3_cleardb_bucket_name = default_configs.get("s3_cleardb_bucket_name", None)
        if self.s3_cleardb_bucket_name is None:
            raise RuntimeError(
                f's3_cleardb_bucket_name is missing from the configs {fc_config_filename}'
            )

        # Parse admin discord IDs
        fc_admin_ids = default_configs.get("fc_admin_ids", None)
        if fc_admin_ids is not None:
            self.fc_admin_ids = [
                int(i.strip())
                for i in fc_admin_ids.split(',')
            ]
        else:
            LOG.info("No admin IDs configured. Auto-approve will be disabled.")
            self.fc_admin_ids = []

        # Set flag
        self.initialized = True

    def __getattr__(self, name):
        if name not in self.combined_configs:
            raise ValueError(f"{name} not found in FC config file ")
        return self.combined_configs.get(name, None)


fc_config_filename = os.environ.get('AX_FC_CONFIG', '.fcconfig')
FC_CONFIG = FCConfig(fc_config_filename, ENV)
