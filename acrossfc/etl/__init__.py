import click
import logging

# Local
from acrossfc import ROOT_LOG
from acrossfc.core.model import CommandConfig
from .update_fflogs_fc import update_fflogs_fc
from .fc_clears_etl import fc_clears_etl
from .fc_roster_etl import fc_roster_etl


@click.group()
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False,
              help="Turn on verbose logging")
def etl(verbose):
    if verbose:
        ROOT_LOG.setLevel(logging.DEBUG)


NAME_TO_CMD_CONFIG_MAP = {
    'update-fflogs-fc': CommandConfig(
        update_fflogs_fc,
        'Triggers an update on the FC roster on FFLogs'
    ),
    'fc-roster-etl': CommandConfig(
        fc_roster_etl,
        'Runs the FC roster ETL job'
    ),
    'clears-etl': CommandConfig(
        fc_clears_etl,
        'Runs the FFLogs clear data ETL job'
    ),
}

for cmd_name, cmd_cfg in NAME_TO_CMD_CONFIG_MAP.items():
    func = cmd_cfg.func
    etl.command(name=cmd_name, help=cmd_cfg.help)(func)
