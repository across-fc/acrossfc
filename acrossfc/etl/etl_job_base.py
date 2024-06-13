# stdlib
from typing import Optional

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.ext.google_cloud_client import GC_CLIENT
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT


class ETLJob:
    def __init__(
        self,
        fc_config_filename: str = '.fcconfig',
        gc_creds_filename: str = '.gc_creds.json',
        prod: Optional[bool] = False
    ):
        FC_CONFIG.initialize(config_filename=fc_config_filename, production=prod)
        GC_CLIENT.initialize(gc_creds_filename)
        FFLOGS_CLIENT.initialize(
            client_id=FC_CONFIG.fflogs_client_id,
            client_secret=FC_CONFIG.fflogs_client_secret,
        )

    def run(self):
        raise NotImplementedError(f"run() not implemented for {self.__class__.__name__}.")
