import click
import logging
from typing import NamedTuple, Type

# Local
from acrossfc import root_logger
from .update_fflogs_fc import UpdateFFLogsFC
from .fc_clears_etl import FCClearsETL
from .fc_roster_etl import FCRosterETL


@click.group()
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False,
              help="Turn on verbose logging")
@click.option('--fc-config', show_default=True, default='.fcconfig',
              help="Path to the FC config file")
@click.option('--gc-creds', show_default=True, default='.gc_creds.json',
              help="File to read Google API credentials for")
@click.option('-p', '--prod', is_flag=True, show_default=True, default=False,
              help="Run in production mode")
@click.pass_context
def etl(ctx, verbose, prod, fc_config, gc_creds):
    if verbose:
        root_logger.setLevel(logging.DEBUG)
    ctx.obj = {
        'etljob_kwargs': {
            'fc_config_filename': fc_config,
            'gc_creds_filename': gc_creds,
            'prod': prod
        }
    }


class JobConfig(NamedTuple):
    cls: Type
    help: str


CMD_TO_JOB_CONFIG_MAP = {
    'update-fflogs-fc': JobConfig(
        UpdateFFLogsFC,
        'Triggers an update on the FC roster on FFLogs'
    ),
    'fc-roster-etl': JobConfig(
        FCRosterETL,
        'Runs the FC roster ETL job'
    ),
    'clears-etl': JobConfig(
        FCClearsETL,
        'Runs the FFLogs clear data ETL job'
    ),
}

for cmd_name, job_cfg in CMD_TO_JOB_CONFIG_MAP.items():
    job_cls = job_cfg.cls
    etl.command(name=cmd_name, help=job_cfg.help)(
        click.pass_context(
            lambda ctx, job_cls=job_cfg.cls: job_cls(**ctx.obj['etljob_kwargs']).run()
        )
    )
