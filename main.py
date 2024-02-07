# stdlib
import os
import sys
import argparse
import logging
import requests
from typing import Tuple, List

# Local
import reports
from model import (
    GuildMember,
    Clear,
    TRACKED_ENCOUNTERS,
    NAME_TO_TRACKED_ENCOUNTER_MAP
)
from fflogs_client import FFLogsAPIClient
from database import Database

LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(filename)s:%(lineno)d: %(message)s'
logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
ACROSS_FFLOGS_GUILD_ID = 75624


def get_secrets(secrets_folder: str) -> Tuple[str, str]:
    """
    Gets FFLogs API client secrets from the secrets folder.
    The folder should contain a file named client_id, and another file named client_secret.
    """
    client_id_filename = os.path.join(secrets_folder, 'client_id')
    if not os.path.exists(client_id_filename):
        LOG.error(f'Unable to find client ID file {client_id_filename}. Please make sure it exists.')

    with open(client_id_filename, 'r') as f:
        client_id = f.read()

    client_secret_filename = os.path.join(args.secrets_folder, 'client_secret')
    if not os.path.exists(client_secret_filename):
        LOG.error(f'Unable to find client secret file {client_secret_filename}. Please make sure it exists.')

    with open(client_secret_filename, 'r') as f:
        client_secret = f.read()

    return client_id, client_secret


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--secrets_folder',
                        '-s',
                        action='store',
                        type=str, default='.secrets',
                        help="Path to the secrets folder.")
    parser.add_argument('--guild_id',
                        '-g',
                        action='store',
                        type=int,
                        default=ACROSS_FFLOGS_GUILD_ID,
                        help="FFLogs guild ID")
    parser.add_argument('--verbose',
                        '-v',
                        action='store_true',
                        default=False,
                        help="Turn on verbose logging")
    parser.add_argument('--save_db_to_filename',
                        '-w',
                        action='store',
                        default=None,
                        help="Filename to save the database to")
    parser.add_argument('--load_db_from_filename',
                        '-r',
                        action='store',
                        default=None,
                        help="Filename to load the database from")
    parser.add_argument('--encounter',
                        '-e',
                        action='append',
                        required=False,
                        type=str,
                        help="Encounters to filter results down for.")
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('fc_roster', help="Prints the FC roster")
    subparsers.add_parser('clear_chart', help="Prints a chart of clears over time based on the current roster.")
    subparsers.add_parser('clear_order', help="Prints the order of clears based on the current roster.")
    subparsers.add_parser('cleared_roles', help="Prints the cleared roles based on the current roster.")
    subparsers.add_parser('cleared_jobs_by_member', help="Prints the cleared jobs for each member.")
    subparsers.add_parser('who_cleared_recently', help="Prints who cleared a certain encounter recently")
    subparsers.add_parser('update_fflogs', help="Updates the FFLogs FC roster")
    subparsers.add_parser('ppl_without_clear', help="Prints the list of people without a clear of a certain fight.")
    subparsers.add_parser('ppl_with_clear', help="Prints the list of people with a clear of a certain fight.")

    args = parser.parse_args()

    # Verbose logging
    if args.verbose:
        LOG.setLevel(logging.DEBUG)
        logging.getLogger('fflogs_client').setLevel(logging.DEBUG)
        logging.getLogger('database').setLevel(logging.DEBUG)

    if args.command == 'update_fflogs':
        LOG.info('Updating FFLogs FC roster...')
        resp = requests.get('https://www.fflogs.com/guild/update/75624')
        if resp.status_code == 200 and 'success' in resp.text:
            LOG.info('Successful.')
            sys.exit(0)
        else:
            LOG.error(f'Failed: {resp.text}')

    if args.load_db_from_filename is not None:
        LOG.info(f'Loading database from {args.load_db_from_filename}...')
        database = Database.load(args.load_db_from_filename)
    else:
        client_id, client_secret = get_secrets(args.secrets_folder)
        fflogs_client = FFLogsAPIClient(client_id=client_id, client_secret=client_secret)
        fc_roster: List[GuildMember] = fflogs_client.get_fc_roster(args.guild_id)
        fc_clears: List[Clear] = []
        for member in fc_roster:
            fc_clears.extend(fflogs_client.get_clears_for_member(member, TRACKED_ENCOUNTERS))

        database = Database(
            fc_roster,
            fc_clears,
            guild_rank_filter=lambda rank: rank != 7)
        if args.save_db_to_filename is not None:
            LOG.info(f'Saving database to {args.save_db_to_filename}...')
            database.save(args.save_db_to_filename)
    
    # Get encounters filter
    if args.encounter is not None:
        encounters = [NAME_TO_TRACKED_ENCOUNTER_MAP[e] for e in args.encounter]
    else:
        encounters = TRACKED_ENCOUNTERS

    if args.command is None:
        reports.clear_rates(database)
    elif args.command == 'fc_roster':
        reports.fc_roster(database)
    elif args.command == 'clear_chart':
        reports.clear_chart(database)
    elif args.command == 'cleared_roles':
        reports.cleared_roles(database)
    elif args.command == 'clear_order':
        reports.clear_order(database, encounters)
    elif args.command == 'cleared_jobs_by_member':
        reports.cleared_jobs_by_member(database, encounters)
    elif args.command == 'ppl_with_clear':
        reports.ppl_with_clear(database, encounters)
    elif args.command == 'ppl_without_clear':
        reports.ppl_without_clear(database, encounters)
    elif args.command == 'who_cleared_recently':
        reports.who_cleared_recently(database, encounters)
    else:
        raise RuntimeError(f'Unrecognized command: {args.command}')
