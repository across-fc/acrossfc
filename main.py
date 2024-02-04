# stdlib
import os
import argparse
import logging
from typing import Tuple, Dict

# 3rd-party
from tabulate import tabulate

# Local
from model import TrackedEncounter, ClearRate, TRACKED_ENCOUNTERS
from fflogs_client import FFLogsAPIClient

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
    args = parser.parse_args()

    # Verbose logging
    if args.verbose:
        LOG.setLevel(logging.DEBUG)
        logging.getLogger('fflogs_client').setLevel(logging.DEBUG)

    client_id, client_secret = get_secrets(args.secrets_folder)
    ffl_client = FFLogsAPIClient(client_id=client_id, client_secret=client_secret)

    encounter_clear_rates: Dict[TrackedEncounter, ClearRate] = ffl_client.get_clear_rates(
        args.guild_id,
        guild_rank_filter=lambda rank: rank < 7,
        tracked_encounters=TRACKED_ENCOUNTERS)

    table = [
        [
            encounter.name,
            f"{encounter_clear_rates[encounter].clears} / {encounter_clear_rates[encounter].eligible_members}",
            f"{encounter_clear_rates[encounter].clear_rate * 100:.2f}%"
        ]
        for encounter in TRACKED_ENCOUNTERS
    ]

    print(tabulate(table,
                   headers=['Encounter', 'FC clears', 'FC clear rate']))
