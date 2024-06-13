# 3rd-party
import logging
import requests

# Local
from acrossfc.core.config import FC_CONFIG
from .etl_job_base import ETLJob

LOG = logging.getLogger(__name__)


class UpdateFFLogsFC(ETLJob):
    def run(self):
        resp = requests.get(
            f"https://www.fflogs.com/guild/update/{FC_CONFIG.fflogs_guild_id}"
        )
        if resp.status_code == 200 and "success" in resp.text:
            LOG.info("Successfully updated FC roster in FFLogs.")
        else:
            raise RuntimeError(f"Failed: {resp.text}")
