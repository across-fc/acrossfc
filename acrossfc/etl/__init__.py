import click
import logging
from typing import NamedTuple, Callable

# Local
from acrossfc import root_logger
from .update_fflogs_fc import update_fflogs_fc
from .fc_clears_etl import fc_clears_etl
from .fc_roster_etl import fc_roster_etl


@click.group()
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False,
              help="Turn on verbose logging")
def etl(verbose):
    if verbose:
        root_logger.setLevel(logging.DEBUG)


class JobConfig(NamedTuple):
    func: Callable
    help: str


CMD_TO_JOB_CONFIG_MAP = {
    'update-fflogs-fc': JobConfig(
        update_fflogs_fc,
        'Triggers an update on the FC roster on FFLogs'
    ),
    'fc-roster-etl': JobConfig(
        fc_roster_etl,
        'Runs the FC roster ETL job'
    ),
    'clears-etl': JobConfig(
        fc_clears_etl,
        'Runs the FFLogs clear data ETL job'
    ),
}

for cmd_name, job_cfg in CMD_TO_JOB_CONFIG_MAP.items():
    job_func = job_cfg.func
    etl.command(name=cmd_name, help=job_cfg.help)(job_func)
