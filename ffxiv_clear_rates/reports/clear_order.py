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
    clear_order = database.get_clear_order()

    buffer = StringIO()
    for i, encounter in enumerate(encounters):
        if i > 0:
            buffer.write('\n\n')

        buffer.write(f'[{encounter.name}]')
        buffer.write('\n\n')
        table = []
        for i, datapoint in enumerate(clear_order[encounter.name]):
            table.append([
                f'{i+1} ',
                datapoint[0],
                ', '.join(sorted([member.name for member in datapoint[1]]))
            ])
        buffer.write(tabulate(table,
                              headers=['Order', 'Clear Date', 'Member(s)'],
                              tablefmt="simple"))

    return Report(
        ':first_place:',
        'Clear Order:',
        None,
        buffer.getvalue(),
        None
    )
