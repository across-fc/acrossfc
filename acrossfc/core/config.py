# stdlib
import configparser


class FCConfig:
    """
    Loads FC configs from a file.

    Expected structure:

        [DEFAULT]
        FFLogsGuildID = #####
        ExcludeGuildRanks = #,##,...    (optional)
        DiscordWebhookURL = ...         (optional)

    """
    def __init__(self):
        self.initialized = False

    def initialize(self, config_filename: str = ".fcconfig", production: bool = False):
        configs = configparser.ConfigParser()
        configs.read(config_filename)
        default_configs = configs["DEFAULT"]
        if production:
            default_configs.update(configs["PROD"])
        self.combined_configs = default_configs

        # Assert we have FFLogs client credentials
        fflogs_client_id = default_configs.get("fflogs_client_id", None)
        fflogs_client_secret = default_configs.get("fflogs_client_secret", None)
        if fflogs_client_id is None or fflogs_client_secret is None:
            raise RuntimeError(
                f'"FFLogs API credentials are missing from the [DEFAULT] section in {config_filename}.'
            )

        # Parse FFLogs guild ID
        self.fflogs_guild_id = int(default_configs.get("fflogs_guild_id", -1))
        if self.fflogs_guild_id == -1:
            raise RuntimeError(
                f'"FFLogsGuildID" is missing from the [DEFAULT] section in {config_filename}.'
            )

        # Parse guild ranks to exclude
        exclude_guild_ranks_str = default_configs.get("exclude_guild_ranks", "")
        self.exclude_guild_ranks = set(
            int(s.strip())
            for s in exclude_guild_ranks_str.split(",")
            if s.strip() != ""
        )

        # Set flag
        self.initialized = True

    def __getattr__(self, name):
        if not self.initialized:
            raise RuntimeError("FCConfig is not initialized yet. Call initialize()")
        return self.combined_configs.get(name, None)


FC_CONFIG = FCConfig()
