# stdlib
from io import StringIO
from typing import List
from datetime import date

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TrackedEncounter
from .report import Report


class PeopleWithoutClear(Report):
    def __init__(self, database: Database, encounters: List[TrackedEncounter]):
        buffer = StringIO()

        for i, encounter in enumerate(encounters):
            if i > 0:
                buffer.write('\n\n')

            uncleared_members = database.get_uncleared_members_by_encounter(encounter)
            sorted_names = sorted([
                f"{member.name}"
                for member in uncleared_members
            ])

            buffer.write(f'{encounter.name} ({len(sorted_names)})')
            buffer.write('\n-------------------------------------------------\n')
            for i, name in enumerate(sorted_names):
                if i > 0:
                    buffer.write('\n')
                buffer.write(f"{i+1:>2}: {name}")

        super().__init__(
            ':no_entry_sign:',
            f'People who have NOT cleared: {date.today()}',
            'Names displayed in alphabetical order',
            buffer.getvalue(),
            None
        )
