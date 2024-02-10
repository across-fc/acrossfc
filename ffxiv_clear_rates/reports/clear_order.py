# stdlib
from io import StringIO
from typing import List

# 3rd-party
from tabulate import tabulate

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TrackedEncounter
from .report import Report


def clear_order(database: Database, encounters: List[TrackedEncounter]) -> Report:
    clear_chart = database.get_clear_chart()

    buffer = StringIO()
    for i, encounter in enumerate(encounters):
        if i > 0:
            buffer.write('\n\n')

        buffer.write(encounter.name)
        buffer.write('\n-----------------------\n')
        table = []
        current_clearees = set()
        for i, datapoint in enumerate(clear_chart[encounter]):
            table.append([
                i+1,
                datapoint[0],
                ', '.join([member.name for member in (datapoint[1] ^ current_clearees)])
            ])
            current_clearees = datapoint[1]
        buffer.write(tabulate(table, tablefmt="tsv"))

    return Report(
        ':first_place:',
        'Clear Order:',
        None,
        buffer.getvalue(),
        None
    )
