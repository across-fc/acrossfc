# stdlib
import os
import json
import argparse
import logging
from datetime import timedelta
from typing import Tuple, Dict, List
from collections import defaultdict

# 3rd-party
from tabulate import tabulate

# Local
from model import TrackedEncounter, GuildMember, Clear, ClearRate, Job, JobCategory, TRACKED_ENCOUNTERS
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


def print_clear_rates(database: Database):
    clear_rates: Dict[TrackedEncounter, ClearRate] = database.get_clear_rates(
        tracked_encounters=TRACKED_ENCOUNTERS)

    table = [
        [
            encounter.name,
            f"{clear_rates[encounter].clears} / {clear_rates[encounter].eligible_members}",
            f"{clear_rates[encounter].clear_rate * 100:.2f}%"
        ]
        for encounter in TRACKED_ENCOUNTERS
    ]

    print()
    print(tabulate(table,
                   headers=['Encounter', 'FC clears', 'FC clear rate']))


def print_ppl_without_encounter(database: Database, encounter: TrackedEncounter):
    uncleared_members = database.get_uncleared_members_by_encounter(encounter)

    print()
    print(f'People who have not cleared {encounter.name}')
    print(json.dumps([
        f"{member.name} ({member.id})"
        for member in uncleared_members
    ], indent=4))


def print_clear_chart(database: Database):
    clear_chart = database.get_clear_chart()

    # Change member list to number of members
    for encounter in clear_chart:
        number_of_data_points = len(clear_chart[encounter])
        for i in range(number_of_data_points):
            datapoint = clear_chart[encounter][i]
            clear_chart[encounter][i] = (
                datapoint[0], len(datapoint[1])
            )

    earliest_date = sorted([
        clear_chart[encounter][0][0]
        for encounter in clear_chart
    ])[0]
    latest_date = sorted([
        clear_chart[encounter][-1][0]
        for encounter in clear_chart
    ])[-1]

    table = []
    current_date = earliest_date
    while current_date <= latest_date:
        LOG.debug(f'Processing {current_date.isoformat()}...')
        clears = [
            next(
                (
                    datapoint[1]
                    for datapoint in reversed(clear_chart[encounter])
                    if datapoint[0] <= current_date
                ),
                0
            )
            for encounter in clear_chart
        ]
        table.append([current_date.isoformat()] + clears)
        current_date += timedelta(days=1)

    print(tabulate(table,
                   headers=[encounter.name for encounter in clear_chart],
                   tablefmt="tsv"))


def print_clear_order(database: Database):
    clear_chart = database.get_clear_chart()

    for encounter in clear_chart:
        print()
        print(encounter.name)
        print('-----------------------')
        table = []
        current_clearees = set()
        for i, datapoint in enumerate(clear_chart[encounter]):
            table.append([
                i+1,
                datapoint[0],
                ', '.join([member.name for member in (datapoint[1] ^ current_clearees)])
            ])
            current_clearees = datapoint[1]
        print(tabulate(table, tablefmt="tsv"))


def print_cleared_roles(database: Database):
    cleared_jobs = database.get_cleared_jobs()
    table = []
    for encounter in cleared_jobs:
        cleared_cat_counts = {
            cat: 0
            for cat in JobCategory
        }
        for cleared_job in cleared_jobs[encounter]:
            cleared_cat_counts[cleared_job[1].main_category] += 1
            if cleared_job[1].sub_category is not None:
                cleared_cat_counts[cleared_job[1].sub_category] += 1

        table.append([encounter.name] + [cleared_cat_counts[cat] for cat in JobCategory])

    print(tabulate(table, headers=[cat.name for cat in JobCategory], tablefmt="tsv"))


def print_cleared_jobs_by_member(database: Database):
    cleared_jobs = database.get_cleared_jobs()
    for encounter in cleared_jobs:
        # Manually do a group-by. itertools.groupby seems to be oddly random...
        member_cleared_jobs: Dict[GuildMember, List[Job]] = defaultdict(list)
        for member_cleared_job in cleared_jobs[encounter]:
            member_cleared_jobs[member_cleared_job[0]].append(member_cleared_job[1])
        member_cleared_jobs = sorted(member_cleared_jobs.items(), key=lambda i: len(i[1]), reverse=True)

        print()
        print(encounter.name)
        print('-------------------------')
        for i, item in enumerate(member_cleared_jobs):
            print(f'{i:>2}: {item[0].name} ({len(item[1])}: {", ".join(job.acronym for job in item[1])})')


def print_who_cleared_today(database: Database, encounter: TrackedEncounter):
    encounter_clear_chart = database.get_clear_chart()[encounter]

    print(encounter_clear_chart[-1][0].isoformat())
    print(encounter_clear_chart[-1][1] ^ encounter_clear_chart[-2][1])


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
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('clear_chart', help="Prints a chart of clears over time based on the current roster.")
    subparsers.add_parser('clear_order', help="Prints the order of clears based on the current roster.")
    subparsers.add_parser('cleared_roles', help="Prints the cleared roles based on the current roster.")
    subparsers.add_parser('cleared_jobs_by_member', help="Prints the cleared jobs for each member.")
    
    # Toxic
    toxic = subparsers.add_parser('ppl_without_clear',
                                  help="Prints the list of people without a clear of a certain fight.")
    toxic.add_argument('--encounter', '-e', action='store', required=True, type=str,
                       help=f"Encounter to check stats for. Possible values: "
                       "{', '.join(e.name for e in TRACKED_ENCOUNTERS)}")

    args = parser.parse_args()

    # Verbose logging
    if args.verbose:
        LOG.setLevel(logging.DEBUG)
        logging.getLogger('fflogs_client').setLevel(logging.DEBUG)
        logging.getLogger('database').setLevel(logging.DEBUG)

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
            guild_rank_filter=lambda rank: rank < 7)
        if args.save_db_to_filename is not None:
            LOG.info(f'Saving database to {args.save_db_to_filename}...')
            database.save(args.save_db_to_filename)

    if args.command is None:
        print_clear_rates(database)
    elif args.command == 'clear_chart':
        print_clear_chart(database)
    elif args.command == 'clear_order':
        print_clear_order(database)
    elif args.command == 'cleared_roles':
        print_cleared_roles(database)
    elif args.command == 'cleared_jobs_by_member':
        print_cleared_jobs_by_member(database)
    elif args.command == 'ppl_without_clear':
        print_ppl_without_encounter(database, args.encounter)

    from model import P12S
    print_who_cleared_today(database, P12S)
