import click
import logging

# Local
from acrossfc import root_logger
from acrossfc.core.database import ClearDatabase
from acrossfc.core.model import (
    ALL_TRACKED_ENCOUNTER_NAMES,
    TIER_NAME_TO_ENCOUNTER_NAMES_MAP,
    NAME_TO_JOB_CATEGORIES_MAP,
    TLA_TO_JOB_MAP,
    JOBS,
)
from .clear_rates import ClearRates
from .clear_chart import ClearChart
from .clear_order import ClearOrder
from .cleared_jobs_by_member import ClearedJobsByMember
from .cleared_roles import ClearedRoles
from .fc_roster import FCRoster
from .legends import Legends
from .ppl_with_clear import PeopleWithClear
from .ppl_without_clear import PeopleWithoutClear
from .who_cleared_recently import WhoClearedRecently

LOG = logging.getLogger(__name__)


@click.command()
@click.argument('report')
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False,
              help="Turn on verbose logging")
@click.option('-f', '--cleardb-file', required=True,
              help="File to read or write the clear database to")
@click.option('-e', '--encounter', multiple=True,
              type=click.Choice(ALL_TRACKED_ENCOUNTER_NAMES, case_sensitive=False),
              help="Filter results by encounter")
@click.option('-t', '--tier',
              type=click.Choice(TIER_NAME_TO_ENCOUNTER_NAMES_MAP.keys(), case_sensitive=False),
              help="Filter results by tier. Overrides --encounter")
@click.option('-j', '--job', multiple=True,
              type=click.Choice(TLA_TO_JOB_MAP.keys(), case_sensitive=False),
              help="Filter results by job")
@click.option('-jr', '--job-role', multiple=True,
              type=click.Choice(NAME_TO_JOB_CATEGORIES_MAP.keys(), case_sensitive=False),
              help="Filter results by role. Overrides --job")
@click.option('--include-echo', is_flag=True, show_default=True, default=False,
              help="Include echo clears")
def axr(report, verbose, cleardb_file, encounter, tier, job, job_role, include_echo):
    if verbose:
        root_logger.setLevel(logging.DEBUG)

    database = ClearDatabase(db_filename=cleardb_file)

    encounter_names = ALL_TRACKED_ENCOUNTER_NAMES
    if tier is not None:
        encounter_names = TIER_NAME_TO_ENCOUNTER_NAMES_MAP[tier]
    elif len(encounter) > 0:
        encounter_names = encounter

    jobs = JOBS
    if len(job_role) > 0:
        jobs = [
            j for j in JOBS
            if j.main_category_id in job_role or j.sub_category_id in job_role
        ]
    elif len(job) > 0:
        jobs = [TLA_TO_JOB_MAP[j] for j in job]

    if report == "clear_rates":
        report = ClearRates(database, include_echo=include_echo)
    elif report == "fc_roster":
        report = FCRoster(database)
    elif report == "legends":
        report = Legends(database)
    elif report == "clear_chart":
        report = ClearChart(database, encounter_names, include_echo=include_echo)
    elif report == "cleared_roles":
        report = ClearedRoles(database, include_echo=include_echo)
    elif report == "clear_order":
        report = ClearOrder(database, encounter_names, include_echo=include_echo)
    elif report == "cleared_jobs_by_member":
        report = ClearedJobsByMember(database, encounter_names, jobs, include_echo=include_echo)
    elif report == "ppl_with_clear":
        report = PeopleWithClear(database, encounter_names, include_echo=include_echo)
    elif report == "ppl_without_clear":
        report = PeopleWithoutClear(database, encounter_names, include_echo=include_echo)
    elif report == "who_cleared_recently":
        report = WhoClearedRecently(database, encounter_names, include_echo=include_echo)
    else:
        raise RuntimeError(f"Unrecognized report: {report}")
    pass

    click.echo(report.to_cli_str())

    return report.to_dict()
