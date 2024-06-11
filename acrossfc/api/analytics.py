import click
import logging
from typing import List

# 3rd party
import requests

# Local
from acrossfc import root_logger
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.database import ClearDatabase
from acrossfc.core.model import (
    Member,
    Clear,
    ACTIVE_TRACKED_ENCOUNTERS,
    ALL_TRACKED_ENCOUNTER_NAMES,
    ACTIVE_TRACKED_ENCOUNTER_NAMES,
    TIER_NAME_TO_ENCOUNTER_NAMES_MAP,
    TLA_TO_JOB_MAP,
    JOBS,
)
import acrossfc.ext.s3_client as S3Client
from acrossfc.ext.fflogs_client import FFLogsAPIClient
from acrossfc.ext.google_cloud_client import GCClient

LOG = logging.getLogger(__name__)


@click.group()
@click.option('-p', '--prod', is_flag=True, show_default=True,
              default=False,
              help="Run in production mode")
@click.option('-v', '--verbose', is_flag=True, show_default=True,
              default=False,
              help="Turn on verbose logging")
@click.option('--fc-config', show_default=True,
              default='.fcconfig',
              help="Path to the FC config file")
@click.option('--gc-creds-file', show_default=True,
              default='.gc_creds.json',
              help="File to read Google API credentials for")
@click.option('-db', '--database',
              help="Path to the database file to read or write to")
@click.pass_context
def axr(ctx, prod, verbose, fc_config, gc_creds_file, database):
    if verbose:
        root_logger.setLevel(logging.DEBUG)
    FC_CONFIG.initialize(config_filename=fc_config, production=prod)
    GCClient.initialize(gc_creds_file)
    ctx.obj = {
        'database': database
    }


@axr.command()
def update_fflogs():
    resp = requests.get(
        f"https://www.fflogs.com/guild/update/{FC_CONFIG.fflogs_guild_id}"
    )
    if resp.status_code == 200 and "success" in resp.text:
        click.echo("Successful.")
        return
    else:
        raise RuntimeError(f"Failed: {resp.text}")


@axr.command()
@click.pass_context
def extract_fflogs_data(ctx):
    click.echo("Extract FFLogs data")
    fflogs_client = FFLogsAPIClient(
        client_id=FC_CONFIG.fflogs_client_id,
        client_secret=FC_CONFIG.fflogs_client_secret,
    )

    fc_roster: List[Member] = fflogs_client.get_fc_roster(
        guild_id=FC_CONFIG.fflogs_guild_id,
        guild_rank_filter=lambda rank: rank not in FC_CONFIG.exclude_guild_ranks,
    )
    fc_clears: List[Clear] = []
    for member in fc_roster:
        fc_clears.extend(
            fflogs_client.get_clears_for_member(member, ACTIVE_TRACKED_ENCOUNTERS)
        )

    local_db_filename = ctx.obj['database']
    database = ClearDatabase.from_fflogs(fc_roster, fc_clears)
    database.save(local_db_filename)
    S3Client.upload_clear_database(local_db_filename)


@axr.command()
def fc_roster():
    click.echo("fc_roster")


@axr.command()
def clear_rates():
    click.echo("clear_rates")


@axr.command()
def clear_chart():
    click.echo("clear_chart")


@axr.command()
def clear_order():
    click.echo("clear_order")


@axr.command()
def cleared_roles():
    click.echo("cleared_roles")


@axr.command()
def cleared_jobs_by_member():
    click.echo("cleared_jobs_by_member")


@axr.command()
def who_cleared_recently():
    click.echo("who_cleared_recently")


@axr.command()
def ppl_with_clear():
    click.echo("ppl_with_clear")


@axr.command()
def ppl_without_clear():
    click.echo("ppl_without_clear")
