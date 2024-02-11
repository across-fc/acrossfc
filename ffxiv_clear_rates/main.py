# stdlib
import sys
import argparse
import logging
import requests
from typing import List

# Local
from .model import (
    Member,
    Clear,
    TRACKED_ENCOUNTERS,
    NAME_TO_TRACKED_ENCOUNTER_MAP
)
from ffxiv_clear_rates.fflogs_client import FFLogsAPIClient
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.config import FC_CONFIG
from ffxiv_clear_rates import reports
from ffxiv_clear_rates.reports import Report

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def run():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('--verbose',
                               '-v',
                               action='store_true',
                               default=False,
                               help="Turn on verbose logging")
    common_parser.add_argument('--save_db_to_filename',
                               '-w',
                               action='store',
                               default=None,
                               help="Filename to save the database to")
    common_parser.add_argument('--load_db_from_filename',
                               '-r',
                               action='store',
                               default=None,
                               help="Filename to load the database from")
    common_parser.add_argument('--encounter',
                               '-e',
                               action='append',
                               type=str,
                               help="Encounters to filter results down for.")
    common_parser.add_argument('--publish',
                               '-p',
                               action='store_true',
                               default=False,
                               help="Specifies whether to publish results to the webhook link or not.")

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('clear_rates',
                          parents=[common_parser],
                          help="Prints the FC clear rates.")
    subparsers.add_parser('fc_roster',
                          parents=[common_parser],
                          help="Prints the FC roster.")
    subparsers.add_parser('clear_chart',
                          parents=[common_parser],
                          help="Prints a chart of clears over time based on the current roster.")
    subparsers.add_parser('clear_order',
                          parents=[common_parser],
                          help="Prints the order of clears based on the current roster.")
    subparsers.add_parser('cleared_roles',
                          parents=[common_parser],
                          help="Prints the cleared roles based on the current roster.")
    subparsers.add_parser('cleared_jobs_by_member',
                          parents=[common_parser],
                          help="Prints the cleared jobs for each member.")
    subparsers.add_parser('who_cleared_recently',
                          parents=[common_parser],
                          help="Prints who cleared a certain encounter recently")
    subparsers.add_parser('update_fflogs',
                          parents=[common_parser],
                          help="Updates the FFLogs FC roster")
    subparsers.add_parser('ppl_without_clear',
                          parents=[common_parser], 
                          help="Prints the list of people without a clear of a certain fight.")
    subparsers.add_parser('ppl_with_clear',
                          parents=[common_parser], 
                          help="Prints the list of people with a clear of a certain fight.")

    args = parser.parse_args()

    # Verbose logging
    if args.verbose:
        LOG.setLevel(logging.DEBUG)
        logging.getLogger('fflogs_client').setLevel(logging.DEBUG)
        logging.getLogger('database').setLevel(logging.DEBUG)

    if args.command == 'update_fflogs':
        LOG.info('Updating FFLogs FC roster...')
        resp = requests.get(f'https://www.fflogs.com/guild/update/{FC_CONFIG.fflogs_guild_id}')
        if resp.status_code == 200 and 'success' in resp.text:
            LOG.info('Successful.')
            sys.exit(0)
        else:
            LOG.error(f'Failed: {resp.text}')
            sys.exit(1)

    if args.load_db_from_filename is not None:
        LOG.info(f'Loading database from {args.load_db_from_filename}...')
        database = Database(db_filename=args.load_db_from_filename)
    else:
        fflogs_client = FFLogsAPIClient(client_id=FC_CONFIG.fflogs_client_id,
                                        client_secret=FC_CONFIG.fflogs_client_secret)

        fc_roster: List[Member] = fflogs_client.get_fc_roster(
            guild_id=FC_CONFIG.fflogs_guild_id,
            guild_rank_filter=lambda rank: rank not in FC_CONFIG.exclude_guild_ranks)
        fc_clears: List[Clear] = []
        for member in fc_roster:
            fc_clears.extend(fflogs_client.get_clears_for_member(member, TRACKED_ENCOUNTERS))

        database = Database.from_fflogs(fc_roster, fc_clears)

        if args.save_db_to_filename is not None:
            LOG.info(f'Saving database to {args.save_db_to_filename}...')
            database.save(args.save_db_to_filename)

    # Sanitize encounter input filter
    encounters = TRACKED_ENCOUNTERS
    if args.encounter is not None:
        for e_str in args.encounter:
            if e_str not in NAME_TO_TRACKED_ENCOUNTER_MAP:
                raise RuntimeError(f'{e_str} is not a tracked encounter.')

        encounters = [NAME_TO_TRACKED_ENCOUNTER_MAP[e_str] for e_str in args.encounter]

    if args.command == 'clear_rates':
        report: Report = reports.clear_rates(database)
    elif args.command == 'fc_roster':
        report: Report = reports.fc_roster(database)
    elif args.command == 'clear_chart':
        report: Report = reports.clear_chart(database)
    elif args.command == 'cleared_roles':
        report: Report = reports.cleared_roles(database)
    elif args.command == 'clear_order':
        report: Report = reports.clear_order(database, encounters)
    elif args.command == 'cleared_jobs_by_member':
        report: Report = reports.cleared_jobs_by_member(database, encounters)
    elif args.command == 'ppl_with_clear':
        report: Report = reports.ppl_with_clear(database, encounters)
    elif args.command == 'ppl_without_clear':
        report: Report = reports.ppl_without_clear(database, encounters)
    elif args.command == 'who_cleared_recently':
        report: Report = reports.who_cleared_recently(database, encounters)
    else:
        raise RuntimeError(f'Unrecognized command: {args.command}')

    # Publish results
    print(report.to_cli_str())
    print()

    if args.publish:
        if FC_CONFIG.discord_webhook_url is None:
            LOG.warning("Unable to publish report to Discord webhook. Please configure it in .fcconfig.")
        else:
            resp = requests.post(FC_CONFIG.discord_webhook_url, data={
                'content': report.to_discord_str()
            })
            if resp.status_code != 204:
                raise RuntimeError(f"Unable to publish report to Discord webhook URL ({resp.status_code}): {resp.text}")

            LOG.info("Report published to Discord webhook.")


if __name__ == "__main__":
    run()
