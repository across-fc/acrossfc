# stdlib
from typing import List

# 3rd-party
from tabulate import tabulate

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TrackedEncounter


def clear_order(database: Database, encounters: List[TrackedEncounter]):
    clear_chart = database.get_clear_chart()

    for encounter in encounters:
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
