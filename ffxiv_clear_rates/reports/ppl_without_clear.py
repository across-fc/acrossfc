# stdlib
from typing import List

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TrackedEncounter


def ppl_without_clear(database: Database, encounters: List[TrackedEncounter]):
    for encounter in encounters:
        uncleared_members = database.get_uncleared_members_by_encounter(encounter)
        sorted_names = sorted([
            f"{member.name} ({member.id})"
            for member in uncleared_members
        ])

        print()
        print(f'People who have not cleared {encounter.name}')
        print('-------------------------------------------------')
        for i, name in enumerate(sorted_names):
            print(f"{i+1:>2}: {name}")
