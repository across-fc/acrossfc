import click
import logging
from typing import List

# 3rd party
import requests

# Local
from acrossfc import root_logger, reports
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.database import ClearDatabase
from acrossfc.core.model import (
    Member,
    Clear,
    ACTIVE_TRACKED_ENCOUNTERS,
    ALL_TRACKED_ENCOUNTER_NAMES,
    ACTIVE_TRACKED_ENCOUNTER_NAMES,
    TIER_NAME_TO_ENCOUNTER_NAMES_MAP,
    ALL_TIER_NAMES,
    TLA_TO_JOB_MAP,
    JOBS,
)
import acrossfc.ext.s3_client as S3Client
from acrossfc.ext.fflogs_client import FFLogsAPIClient
from acrossfc.ext.google_cloud_client import GCClient

LOG = logging.getLogger(__name__)


@click.group()
@click.option('-p', '--prod', is_flag=True, show_default=True, default=False,
              help="Run in production mode")
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False,
              help="Turn on verbose logging")
@click.option('--fc-config', show_default=True, default='.fcconfig',
              help="Path to the FC config file")
@click.option('--gc-creds-file', show_default=True, default='.gc_creds.json',
              help="File to read Google API credentials for")
def axr(prod, verbose, fc_config, gc_creds_file):
    if verbose:
        root_logger.setLevel(logging.DEBUG)
    FC_CONFIG.initialize(config_filename=fc_config, production=prod)
    GCClient.initialize(gc_creds_file)


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
@click.option('-db', '--cleardb-file', required=True,
              help="File to read or write the clear database to")
def extract_fflogs_data(cleardb_file):
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

    database = ClearDatabase.from_fflogs(fc_roster, fc_clears)
    database.save(cleardb_file)
    S3Client.upload_clear_database(cleardb_file)


@axr.command()
@click.argument('report')
@click.option('-db', '--cleardb-file', required=True,
              help="File to read or write the clear database to")
@click.option('-e', '--encounter', multiple=True,
              type=click.Choice(ALL_TRACKED_ENCOUNTER_NAMES, case_sensitive=False),
              help="Filter results by encounter")
@click.option('-t', '--tier',
              type=click.Choice(ALL_TIER_NAMES, case_sensitive=False),
              help="Filter results by tier")
@click.option('--include-echo', is_flag=True, show_default=True, default=False,
              help="Include echo clears")
def run(report, cleardb_file, encounter, tier, include_echo):
    database = ClearDatabase(db_filename=cleardb_file)

    encounter_names = ALL_TRACKED_ENCOUNTER_NAMES
    if len(encounter) > 0:
        for e in encounter:
            if e not in ALL_TRACKED_ENCOUNTER_NAMES:
                raise RuntimeError(f"{e} is not a tracked encounter.")
        encounter_names = encounter

    if tier is not None:
        if tier not in ALL_TIER_NAMES:
            raise RuntimeError(f"{t} is not a tracked tier")
        encounter_names = TIER_NAME_TO_ENCOUNTER_NAMES_MAP[tier]

    jobs = JOBS

    if report == "clear_rates":
        report = reports.ClearRates(database, include_echo=include_echo)
    elif report == "fc_roster":
        report = reports.FCRoster(database)
    elif report == "legends":
        report = reports.Legends(database)
    elif report == "clear_chart":
        report = reports.ClearChart(database, encounter_names, include_echo=include_echo)
    elif report == "cleared_roles":
        report = reports.ClearedRoles(database, include_echo=include_echo)
    elif report == "clear_order":
        report = reports.ClearOrder(database, encounter_names, include_echo=include_echo)
    elif report == "cleared_jobs_by_member":
        report = reports.ClearedJobsByMember(database, encounter_names, jobs, include_echo=include_echo)
    elif report == "ppl_with_clear":
        report = reports.PeopleWithClear(database, encounter_names, include_echo=include_echo)
    elif report == "ppl_without_clear":
        report = reports.PeopleWithoutClear(database, encounter_names, include_echo=include_echo)
    elif report == "who_cleared_recently":
        report = reports.WhoClearedRecently(database, encounter_names, include_echo=include_echo)
    else:
        raise RuntimeError(f"Unrecognized report: {report}")
    pass

    click.echo(report.to_cli_str())

    return report.data
