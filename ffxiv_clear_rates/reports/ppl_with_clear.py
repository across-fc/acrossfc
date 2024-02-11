# stdlib
from io import StringIO
from typing import List
from datetime import date

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TrackedEncounter
from .report import Report


def ppl_with_clear(database: Database, encounters: List[TrackedEncounter]) -> Report:
    buffer = StringIO()

    for i, encounter in enumerate(encounters):
        if i > 0:
            buffer.write('\n\n')

        cleared_members = database.get_cleared_members_by_encounter(encounter)
        sorted_names = sorted([
            f"{member.name}"
            for member in cleared_members
        ])

        buffer.write(f'{encounter.name} ({len(sorted_names)})')
        buffer.write('\n-------------------------------------------------\n')
        for i, name in enumerate(sorted_names):
            if i > 0:
                buffer.write('\n')
            buffer.write(f"{i+1:>2}: {name}")

    return Report(
        ':white_check_mark:',
        f'People who have cleared: {date.today()}',
        'Names displayed in alphabetical order',
        buffer.getvalue(),
        None
    )
