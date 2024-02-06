# stdlib
from typing import Dict

# 3rd-party
from tabulate import tabulate

# Local
from database import Database
from model import TrackedEncounter, ClearRate, TRACKED_ENCOUNTERS


def clear_rates(database: Database):
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
