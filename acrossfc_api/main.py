# stdlib
import argparse
import logging
import requests
from typing import List

# Local
from .model import (
    Member,
    Clear,
    ACTIVE_TRACKED_ENCOUNTERS,
    ALL_TRACKED_ENCOUNTER_NAMES,
    ACTIVE_TRACKED_ENCOUNTER_NAMES,
    TIER_NAME_TO_ENCOUNTER_NAMES_MAP,
    TLA_TO_JOB_MAP,
    JOBS,
)
from acrossfc_api.fflogs_client import FFLogsAPIClient
from acrossfc_api.database import Database
from acrossfc_api import reports
from acrossfc_api.config import FC_CONFIG
from acrossfc_api.reports.gapi import GAPI

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def run():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Turn on verbose logging",
    )
    common_parser.add_argument(
        "--fc_config",
        "-c",
        action="store",
        default=".fcconfig",
        help="File to read FC configs from",
    )
    common_parser.add_argument(
        "--gc_creds_file",
        "-s",
        action="store",
        default=".gc_creds.json",
        help="File to read Google API credentials for",
    )
    common_parser.add_argument(
        "--load_db_from_filename",
        "-r",
        action="store",
        default=None,
        help="Filename to load the database from",
    )
    common_parser.add_argument(
        "--save_db_to_filename",
        "-w",
        action="store",
        default=None,
        help="Filename to save the database to",
    )
    common_parser.add_argument(
        "--encounter",
        "-e",
        action="append",
        type=str,
        help="Encounters to filter results down for.",
    )
    common_parser.add_argument(
        "--tier",
        "-t",
        action="store",
        choices=[k.lower() for k in TIER_NAME_TO_ENCOUNTER_NAMES_MAP],
        default=None,
        type=str,
        help="Encounters to filter results down for.",
    )
    common_parser.add_argument(
        "--job",
        "-j",
        action="append",
        type=str,
        help="Jobs to filter results down for.",
    )
    common_parser.add_argument(
        "--with_echo",
        "-we",
        action="store_true",
        default=False,
        help="Specify whether to include clears with echo"
    )
    common_parser.add_argument(
        "--job_role",
        "-jr",
        action="append",
        type=str,
        help="Job roles to filter results down for.",
    )
    common_parser.add_argument(
        "--publish-to-discord",
        "-pd",
        action="store_true",
        default=False,
        help="Specifies whether to publish results to the webhook link or not.",
    )
    common_parser.add_argument(
        "--publish-to-google-drive",
        "-pg",
        action="store_true",
        default=False,
        help="Specifies whether to publish results to Google Drive",
    )
    common_parser.add_argument(
        "--prod",
        action="store_true",
        default=False,
        help="Specifies whether to use production configs",
    )

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "clear_rates", parents=[common_parser], help="Prints the FC clear rates."
    )
    subparsers.add_parser(
        "fc_roster", parents=[common_parser], help="Prints the FC roster."
    )
    subparsers.add_parser(
        "clear_chart",
        parents=[common_parser],
        help="Prints a chart of clears over time based on the current roster.",
    )
    subparsers.add_parser(
        "clear_order",
        parents=[common_parser],
        help="Prints the order of clears based on the current roster.",
    )
    subparsers.add_parser(
        "cleared_roles",
        parents=[common_parser],
        help="Prints the cleared roles based on the current roster.",
    )
    subparsers.add_parser(
        "cleared_jobs_by_member",
        parents=[common_parser],
        help="Prints the cleared jobs for each member.",
    )
    subparsers.add_parser(
        "who_cleared_recently",
        parents=[common_parser],
        help="Prints who cleared a certain encounter recently",
    )
    subparsers.add_parser(
        "update_fflogs", parents=[common_parser], help="Updates the FFLogs FC roster"
    )
    subparsers.add_parser(
        "ppl_without_clear",
        parents=[common_parser],
        help="Prints the list of people without a clear of a certain fight.",
    )
    subparsers.add_parser(
        "ppl_with_clear",
        parents=[common_parser],
        help="Prints the list of people with a clear of a certain fight.",
    )

    args = parser.parse_args()

    FC_CONFIG.initialize(config_filename=args.fc_config, production=args.prod)
    GAPI.initialize(args.gc_creds_file)

    # Verbose logging
    if args.verbose:
        LOG.setLevel(logging.DEBUG)
        logging.getLogger("fflogs_client").setLevel(logging.DEBUG)
        logging.getLogger("database").setLevel(logging.DEBUG)

    # Update FFLogs
    if args.command == "update_fflogs":
        LOG.info("Updating FFLogs FC roster...")
        resp = requests.get(
            f"https://www.fflogs.com/guild/update/{FC_CONFIG.fflogs_guild_id}"
        )
        if resp.status_code == 200 and "success" in resp.text:
            LOG.info("Successful.")
            return
        else:
            raise RuntimeError(f"Failed: {resp.text}")

    # Load the database from a file or from FFLogs
    if args.load_db_from_filename is not None:
        LOG.info(f"Loading database from {args.load_db_from_filename}...")
        database = Database(db_filename=args.load_db_from_filename)
    else:
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

        database = Database.from_fflogs(fc_roster, fc_clears)

        if args.save_db_to_filename is not None:
            LOG.info(f"Saving database to {args.save_db_to_filename}...")
            database.save(args.save_db_to_filename)

    # Sanitize encounter input filter
    encounter_names = ACTIVE_TRACKED_ENCOUNTER_NAMES
    if args.encounter is not None:
        for e_str in args.encounter:
            if e_str not in ALL_TRACKED_ENCOUNTER_NAMES:
                raise RuntimeError(f"{e_str} is not a tracked encounter.")

        encounter_names = args.encounter

    # Tier will override encounters
    if args.tier is not None:
        tier_name = args.tier.upper()
        if tier_name not in TIER_NAME_TO_ENCOUNTER_NAMES_MAP:
            raise RuntimeError(f"{args.tier} is not a tracked tier.")

        encounter_names = TIER_NAME_TO_ENCOUNTER_NAMES_MAP[tier_name]

    # Jobs filter
    jobs = JOBS
    if args.job is not None:
        jobs = [TLA_TO_JOB_MAP[j] for j in args.job]

    # Job roles filter
    if args.job_role is not None:
        jobs = [
            j
            for j in JOBS
            if j.main_category_id in args.job_role or j.sub_category_id in args.job_role
        ]

    # Handle commands
    if args.command == "clear_rates":
        report = reports.ClearRates(database, include_echo=args.with_echo)
    elif args.command == "fc_roster":
        report = reports.FCRoster(database)
    elif args.command == "clear_chart":
        report = reports.ClearChart(database, encounter_names, include_echo=args.with_echo)
    elif args.command == "cleared_roles":
        report = reports.ClearedRoles(database, include_echo=args.with_echo)
    elif args.command == "clear_order":
        report = reports.ClearOrder(database, encounter_names, include_echo=args.with_echo)
    elif args.command == "cleared_jobs_by_member":
        report = reports.ClearedJobsByMember(database, encounter_names, jobs, include_echo=args.with_echo)
    elif args.command == "ppl_with_clear":
        report = reports.PeopleWithClear(database, encounter_names, include_echo=args.with_echo)
    elif args.command == "ppl_without_clear":
        report = reports.PeopleWithoutClear(database, encounter_names, include_echo=args.with_echo)
    elif args.command == "who_cleared_recently":
        report = reports.WhoClearedRecently(database, encounter_names, include_echo=args.with_echo)
    else:
        raise RuntimeError(f"Unrecognized command: {args.command}")

    # Publish results
    print(report.to_cli_str())
    print()

    if args.publish_to_discord:
        if FC_CONFIG.discord_webhook_url is None:
            LOG.warning(
                "Unable to publish report to Discord webhook. Please configure it in .fcconfig."
            )
        else:
            resp = requests.post(
                FC_CONFIG.discord_webhook_url, data={"content": report.to_discord_str()}
            )
            if resp.status_code != 204:
                raise RuntimeError(
                    f"Unable to publish report to Discord webhook URL ({resp.status_code}): {resp.text}"
                )

            LOG.info("Report published to Discord webhook.")

    if args.publish_to_google_drive:
        published = report.publish_to_gsheets()
        if published:
            LOG.info("Report published to Google drive.")

    return report.to_dict()


if __name__ == "__main__":
    run()
