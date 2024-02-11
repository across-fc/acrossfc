# stdlib
import argparse
import logging
import requests
from typing import List

# Local
from .model import (
    Member,
    Clear,
    TRACKED_ENCOUNTERS,
    NAME_TO_TRACKED_ENCOUNTER_MAP,
    TIER_NAME_TO_TRACKED_ENCOUNTERS_MAP
)
from ffxiv_clear_rates.fflogs_client import FFLogsAPIClient
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates import reports
from ffxiv_clear_rates.config import FC_CONFIG
from ffxiv_clear_rates.reports.gapi import GAPI

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def run():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('--verbose',
                               '-v',
                               action='store_true',
                               default=False,
                               help="Turn on verbose logging")
    common_parser.add_argument('--fc_config',
                               '-c',
                               action='store',
                               default='.fcconfig',
                               help="File to read FC configs from")
    common_parser.add_argument('--gc_creds_file',
                               '-s',
                               action='store',
                               default='.gc_creds.json',
                               help="File to read Google API credentials for")
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
    common_parser.add_argument('--tier',
                               '-t',
                               action='store',
                               choices=[k.lower() for k in TIER_NAME_TO_TRACKED_ENCOUNTERS_MAP],
                               default=None,
                               type=str,
                               help="Encounters to filter results down for.")
    common_parser.add_argument('--publish-to-discord',
                               '-pd',
                               action='store_true',
                               default=False,
                               help="Specifies whether to publish results to the webhook link or not.")
    common_parser.add_argument('--publish-to-google-drive',
                               '-pg',
                               action='store_true',
                               default=False,
                               help="Specifies whether to publish results to Google Drive")
    common_parser.add_argument('--prod',
                               action='store_true',
                               default=False,
                               help="Specifies whether to use production configs")

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

    FC_CONFIG.initialize(config_filename=args.fc_config, production=args.prod)
    GAPI.initialize(args.gc_creds_file)

    # Verbose logging
    if args.verbose:
        LOG.setLevel(logging.DEBUG)
        logging.getLogger('fflogs_client').setLevel(logging.DEBUG)
        logging.getLogger('database').setLevel(logging.DEBUG)

    # Update FFLogs
    if args.command == 'update_fflogs':
        LOG.info('Updating FFLogs FC roster...')
        resp = requests.get(f'https://www.fflogs.com/guild/update/{FC_CONFIG.fflogs_guild_id}')
        if resp.status_code == 200 and 'success' in resp.text:
            LOG.info('Successful.')
            return
        else:
            raise RuntimeError(f'Failed: {resp.text}')

    # Load the database from a file or from FFLogs
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

    # Tier will override encounters
    if args.tier is not None:
        encounters = TIER_NAME_TO_TRACKED_ENCOUNTERS_MAP[args.tier.upper()]

    # Handle commands
    if args.command == 'clear_rates':
        report = reports.ClearRates(database)
    elif args.command == 'fc_roster':
        report = reports.FCRoster(database)
    elif args.command == 'clear_chart':
        report = reports.ClearChart(database, encounters)
    elif args.command == 'cleared_roles':
        report = reports.ClearedRoles(database)
    elif args.command == 'clear_order':
        report = reports.ClearOrder(database, encounters)
    elif args.command == 'cleared_jobs_by_member':
        report = reports.ClearedJobsByMember(database, encounters)
    elif args.command == 'ppl_with_clear':
        report = reports.PeopleWithClear(database, encounters)
    elif args.command == 'ppl_without_clear':
        report = reports.PeopleWithoutClear(database, encounters)
    elif args.command == 'who_cleared_recently':
        report = reports.WhoClearedRecently(database, encounters)
    else:
        raise RuntimeError(f'Unrecognized command: {args.command}')

    # Publish results
    print(report.to_cli_str())
    print()

    if args.publish_to_discord:
        if FC_CONFIG.discord_webhook_url is None:
            LOG.warning("Unable to publish report to Discord webhook. Please configure it in .fcconfig.")
        else:
            resp = requests.post(FC_CONFIG.discord_webhook_url, data={
                'content': report.to_discord_str()
            })
            if resp.status_code != 204:
                raise RuntimeError(f"Unable to publish report to Discord webhook URL ({resp.status_code}): {resp.text}")

            LOG.info("Report published to Discord webhook.")

    if args.publish_to_google_drive:
        published = report.publish_to_gsheets()
        if published:
            LOG.info("Report published to Google drive.")


if __name__ == "__main__":
    run()
