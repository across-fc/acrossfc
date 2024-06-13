import click
import logging

# Local
from acrossfc import root_logger
from acrossfc.core.config import FC_CONFIG
from acrossfc.ext.google_cloud_client import GC_CLIENT
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT

from .daily_clears_etl import daily_clears_etl
from .daily_update_fflogs_fc import daily_update_fflogs_fc
from .monthly_fc_roster_etl import monthly_fc_roster_etl


@click.group()
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False,
              help="Turn on verbose logging")
@click.option('-p', '--prod', is_flag=True, show_default=True, default=False,
              help="Run in production mode")
@click.option('--fc-config', show_default=True, default='.fcconfig',
              help="Path to the FC config file")
@click.option('--gc-creds-file', show_default=True, default='.gc_creds.json',
              help="File to read Google API credentials for")
def etl(verbose, prod, fc_config, gc_creds_file):
    if verbose:
        root_logger.setLevel(logging.DEBUG)
    FC_CONFIG.initialize(config_filename=fc_config, production=prod)
    GC_CLIENT.initialize(gc_creds_file)
    FFLOGS_CLIENT.initialize(
        client_id=FC_CONFIG.fflogs_client_id,
        client_secret=FC_CONFIG.fflogs_client_secret,
    )


etl.add_command(daily_update_fflogs_fc)
etl.add_command(daily_clears_etl)
etl.add_command(monthly_fc_roster_etl)
